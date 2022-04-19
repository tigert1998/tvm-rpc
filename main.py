import argparse

from adb_helper.adb import Adb, Android

if __name__ == "__main__":
    parser = argparse.ArgumentParser("")
    parser.add_argument("--serial", default="98281FFAZ009SV")
    parser.add_argument("--skip-copy", action="store_true")
    parser.add_argument('--cmd-args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    adb = Adb(args.serial, False)

    folder = "/data/local/tmp/tvm-rpc-server"
    android = Android(adb)

    if not android.boolean(f"-d {folder}"):
        adb.shell(f"mkdir {folder}")

    if not args.skip_copy:
        adb.push("build/tvm_rpc", f"{folder}")
        adb.push("build/bin/libtvm_runtime.so", f"{folder}")
    adb.shell(f"chmod +x {folder}/tvm_rpc")

    cmd_args = " ".join(list([] if args.cmd_args is None else args.cmd_args))
    cmd = f"LD_LIBRARY_PATH={folder} {folder}/tvm_rpc {cmd_args}"
    print(cmd)

    print(adb.shell(cmd))
