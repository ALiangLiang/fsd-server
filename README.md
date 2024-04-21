# FSD server

## How to use it

### Start the server

You need to copy your nav data from x-plane folder first.
- Custom Data/CIFP/
- Custom Data/earth_nav.dat
- Custom Data/earth_fix.dat

```sh
pipenv shell
pipenv install
python main.py
```

### Connect the server

First, you need to open your Aurora. Then, set the server to your server's IP address. And... Connect!

## Development

You must know the FSD protocol. Some [internet resouce](https://fsd-doc.norrisng.ca/site/) may help you.
But it's not enough. You can decompile some fsd server to know more about the protocol.
The IVAO training server repo has IVAN FSD protocol. You can find it [here](https://github.com/ivao-xa/TrainingServer/tree/7b3dfa5b5376ebec4b20d974416407ccaa157222/TrainingServer).
Use JetBrains dotPeek to decompile the `IVAN.FSD.Protocol.dll` file. The message schema is in the `IVAN.FSD.Protocol.Messages` namespace.

