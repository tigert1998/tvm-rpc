ADB="${ADB:=adb}"
RPC_PORT="${RPC_PORT:=9000}"
TRACKER_PORT="${TRACKER_PORT:=9190}"
SERVER="${SERVER:=hexserver}"
PYTHON="${PYTHON:=python}"
TASKSET="${TASKSET:=80}"
NUM_THREADS="${NUM_THREADS:=1}"

$ADB -s $SERIAL forward tcp:$RPC_PORT tcp:$RPC_PORT
$ADB -s $SERIAL reverse tcp:$TRACKER_PORT tcp:$TRACKER_PORT
ssh -N -L $RPC_PORT:localhost:$RPC_PORT $SERVER &
ssh -N -R $TRACKER_PORT:localhost:$TRACKER_PORT $SERVER &
$PYTHON -m tvm.exec.rpc_tracker --host=0.0.0.0 --port=$TRACKER_PORT &
pid=$!
$PYTHON main.py --serial=$SERIAL --taskset=$TASKSET --num-threads=$NUM_THREADS \
    --cmd-args server --host=0.0.0.0 \
    --port=$RPC_PORT --port-end=$(($RPC_PORT + 1)) \
    --tracker=127.0.0.1:$TRACKER_PORT --key=$KEY &

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

wait $pid
