Server Side
	- OPC-UA Server
	- Subscribes to designated topics on Google PubSub
	- Uses JSON format
Client Side
	- Data Telemetry via Serial and TCP
	- Data Telemetry via GPIO
	- Publishes Data via PubSub

1) Establish Client Side with Standardized format
	- Format:
		- Topic: /<org>/<group>/<dev>/><sub_dev>
		- Data Packet: includes meta section and data section, meta defines 				channel names (with var type), device_id, timestamp, etc... 				while data defines variables using OPC-UA format 
2) Gather Data from remote sources functioning
3) Setup Server Side OPC-UA Server
4) Parse with meta info and data packet
5) Create OPC-UA Device with subfolders and channels embedded
6) Spin up Ignition Server to present data
7) Create config files that can be easily modified
8) Spin Up Flask Server with basic form to modify settings
