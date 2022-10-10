'''
author: Mz1
一个脚本启动的多功能聊天室

架构:
在新线程中启动flask
在主线程中启动websockets
'''

# index.html
index_html = '''
<!DOCTYPE html>
<html>
<head>
	<title>PyChatRoom@Mz1</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, 
									 initial-scale=1.0, 
									 maximum-scale=1.0, 
									 user-scalable=no">
	<!-- 引入jquery和bootstrap -->
	<link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/css/bootstrap.min.css">  
	<script src="https://cdn.staticfile.org/jquery/2.1.1/jquery.min.js"></script>
	<script src="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>

</head>
<body>
<div class='container'>
<h4>当前聊天室: {{ _path }}</h4>

<input id="text" value="">
 <input type="submit" value="send" onclick="start()">
 <input type="submit" value="close" onclick="close()">
<div id="msg"></div>

</div>
	
</body>

<script>
 /**
 0：未连接

1：连接成功，可通讯

2：正在关闭

3：连接已关闭或无法打开
*/

    //创建一个webSocket 实例
    var url = window.location.host.split(':');     // 获取当前路径
    var ip = url[0];
    console.log(ip);
    // 拼接websocket地址
    var _url = "ws://"+ip+":2333" + window.location.pathname;
    var webSocket  = new  WebSocket(_url);

    webSocket.onerror = function (event){
        onError(event);
    };
    // 打开websocket
    webSocket.onopen = function (event){
        onOpen(event);
    };
    //监听消息
    webSocket.onmessage = function (event){
        onMessage(event);
    };
    webSocket.onclose = function (event){
        onClose(event);
    }

    //关闭监听websocket
    function onError(event){
        document.getElementById("msg").innerHTML = "<p>close</p>";
        console.log("error"+event.data);
    };

    function onOpen(event){
        console.log("open:"+sockState());
        document.getElementById("msg").innerHTML = "<p>Connect to Service</p>";
        document.getElementById("msg").innerHTML += '<p>连接到: '+_url+'</p>';
    };
    function onMessage(event){
        console.log("onMessage");
        document.getElementById("msg").innerHTML += "<p>response: "+event.data+"</p>"
    };

    function onClose(event){
        document.getElementById("msg").innerHTML = "<p>close</p>";
        console.log("close: "+sockState());
        webSocket.close();
    }

    function sockState(){
        var status = ['未连接','连接成功，可通讯','正在关闭','连接已关闭或无法打开'];
            return status[webSocket.readyState];
    }



 function start(event){
        console.log(webSocket);
        var msg = document.getElementById('text').value;
        document.getElementById('text').value = '';
        console.log("send:"+sockState());
        console.log("msg="+msg);
        webSocket.send(msg);   // 发送消息
        // document.getElementById("msg").innerHTML += "<p>request: "+msg+"</p>"
    };

    function close(event){
        webSocket.close();
    }
</script>


</html>
'''

from flask import Flask, render_template_string
import asyncio
import websockets
import threading
import time

# Websocket服务端
class WebsocketChatServer():
	def __init__(self):
		self.conn = {}  # 连接字典 房间名:[conn1, conn2]

	async def run(self, port):
		start_server = websockets.serve(self.handler, "", port)
		await start_server
		print(f'  > server start ok! on port {port}')
		await asyncio.Future()           # run forever

	# 处理消息用的handle
	async def handler(self, websocket, path):
		print(f'\n进入房间：{path}')   # 当前房间路径
		if path in self.conn:
			self.conn[path].append(websocket)   # 添加当前连接
		else:
			self.conn[path] = [websocket]    # 添加当前连接
		print(f'当前房间: {self.conn}')
		
		# 循环处理消息
		while True:
			try:
				msg = await websocket.recv()
				# 分发消息给房间里的用户
				for conn in self.conn[path]:
					await conn.send(msg)
			except websockets.ConnectionClosedOK:
				break
			print(f"recv: {msg}")
			
		self.conn[path].remove(websocket)  # 移除连接
		# 判断房间有没有人
		for room in self.conn:
			if self.
		print(self.conn)
		print('  > close a connection')


# 初始化和定义flask
app = Flask(__name__)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
	return render_template_string(index_html, _path=path)    # 捕获一切路径，返回拼接的html文件


# 启动函数
def main():
	# 在新线程中启动flask
	print(app.url_map)
	flask_thread = threading.Thread(target=app.run, args=('0.0.0.0', 5000))
	flask_thread.start()
	
	# 启动websocket server
	print('> starting server...')
	server = WebsocketChatServer()
	tasks = [
		server.run(2333),
	]
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(asyncio.wait(tasks))
	except KeyboardInterrupt:
		for task in asyncio.Task.all_tasks():
			task.cancel()
		loop.stop()
		loop.run_forever()
	loop.close()

if __name__ == '__main__':
	main()
		
