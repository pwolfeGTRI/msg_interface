# skaimsginterface Examples


## Run Listener 

Open terminal and `./attach.sh` into the container and `cd examples`

Run `./example_listener.py tcp` or `./example_listener.py udp`  to listen for the example messages on the protocol you want

Optional Arguments:
- arg to record messages (specify filepath ending in `.skaibin`): 
    
    ```
    --recordfile testfolder/testrecord.skaibin
    ```
- arg to listen on different camera group (default is 0) (number must be from 0 to 99):
    ```
    --camgroup 32
    ```

## Run Sender

Open terminal and `./attach.sh` into the container and `cd examples`

Then run which ever example you want with whatever protocol you want.
see `test_all.sh` for examples or just run that with protocol to send one of each:
- example: `./test_all.sh tcp` 

Optional Arguments:
- arg to dump an example message to example_msg_prints/{msgnamehere}.txt
    ```
    --exampleout
    ```
- arg to change camera group number to send on (number must be from 0 to 99)
    ```
    --camgroup 59
    ```

## Run Replayer

Open terminal and `./attach.sh` into the container and `cd examples`

Example tcp replay

`./replay_skaibin.py filetoreplay.skaibin tcp`

Optional Arguments:
- arg to analyze file message type count only (no replay):
    ```
    --analyzeonly
    ```
- arg to replay on different camera group than original (number must be from 0 to 99):
    ```
    --camgroup 32
    ```