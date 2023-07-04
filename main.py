import re
import os.path as osp
import argparse

from adb_helper.adb import Adb, Android


def parse_cmake_toolchain_file(cmake_cache):
    with open(cmake_cache, "r") as f:
        m = re.search('CMAKE_TOOLCHAIN_FILE:(STRING|FILEPATH)\=.*', f.read())
        line = m.group(0)
        return line[line.find('=') + 1:]


def resolve_necessary_lib(cmake_toolchain_file):
    ndk = cmake_toolchain_file[:cmake_toolchain_file.find("build")]
    return osp.join(ndk, "toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("")
    parser.add_argument("--serial", default="98281FFAZ009SV")
    parser.add_argument("--skip-copy", action="store_true")
    parser.add_argument("--taskset", default="")
    parser.add_argument("--num-threads", default=1, type=int)
    parser.add_argument('--cmd-args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    adb = Adb(args.serial, False)

    folder = "/data/local/tmp/tvm-rpc-server"
    android = Android(adb)

    if not android.boolean(f"-d {folder}"):
        adb.shell(f"mkdir {folder}")
        
    if not args.skip_copy:
        script_folder = osp.dirname(__file__)
        adb.push(osp.join(script_folder, "build/tvm_rpc"), folder)
        adb.push(osp.join(script_folder, "build/bin/libtvm_runtime.so"), folder)
        adb.push(
            resolve_necessary_lib(
                parse_cmake_toolchain_file(osp.join(script_folder, "build/CMakeCache.txt"))),
            folder
        )
    adb.shell(f"chmod +x {folder}/tvm_rpc")
    print(adb.shell(f"ls -lh {folder}"))

    cmd_args = " ".join(list([] if args.cmd_args is None else args.cmd_args))
    taskset = "" if args.taskset == "" else f"taskset {args.taskset}"
    cmd = f"LD_LIBRARY_PATH={folder} TVM_NUM_THREADS={args.num_threads} {taskset} {folder}/tvm_rpc {cmd_args}"
    print(cmd)

    print(adb.shell(cmd))
