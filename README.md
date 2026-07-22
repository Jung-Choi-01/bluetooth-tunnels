## bluetooth-tunnels
a short, blatantly vibe-coded experiment to learn bluetooth reverse engineering in a fun way.
here's a rough explanation of the "stack":

### 1. svelte-kit message sender
send POST requests to a public IP, configurable in message_config.json
i may add more modes in the future. for now we just have range and it sends lots and lots of requests

### 2. flask server to translate rest requests to bluetooth messages
receives POST requests on localhost, and then translates them to bluetooth messages.
since bluetooth protocols are obscured and much more device-specific than i thought, these are set manually in the code. i don't think i would save you much time by trying to do this programmatically.

### 3. expose your localhost somehow
normally, you can do this by port forwarding, but i'm really lazy and use localtunnel. none of their code is included in this project, but you can just run this project and then set localtunnel to the port flask is running on (5000 here).

### steps to run (with my specific setup)
1. start python flask server
2. start localtunnel on port 5000
3. find a friend, give them the github page, inform them to supply the URL localtunnel gave me
4. woahhhhh wtf wow!!

### how can i modify this for my devices?
yeah sure, if you feel like figuring out your target device's mac address and the rules it has around the connection UUID. here's how i figured those out for [my specific device](https://www.amazon.com/dp/B0GD7MMP69):
1. turn on bluetooth hci snooping in android developer settings
2. make a few requests to your device
3. run `adb bugreport`
4. find the snoop log report (`btsnooz.hci`, in my case), and open it in wireshark to find your device's MAC
5. connect to the MAC with python's `bleak` package to find available connection uuid's
6. mess around with the availabile uuid's until you figure out your device's rules. mine were that a two-way handshake has to be established: we have to agree to listen to its notify, and only then are we allowed to write values to it.
7. find a couple sample requests in wireshark and use their values as a template to see if you can get your device to do what you want it to from python

there's probably way better ways to do this, but i'm a beginner and was curious about bluetooth. thanks for reading!