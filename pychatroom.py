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
<div id='header'>
	<h4>说明：你可以在网址后面加任意字符进入任意房间，例如加上"cybersecurity"变成"http://xxxx.com:5000/cybersecurity"</h4>
	<h4>你也可以什么都不做，就在大厅聊天</h4>
	<h3>当前聊天室: {{ _path }}</h3>
</div>

<hr/>

<div id="chat">
	<input id="text" value="">
	<input type="submit" value="send" onclick="start()">
	<input type="submit" value="close" onclick="close()">
</div>

<hr/>
	
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
	// 获取用户输入名字
	var uname = prompt("请输入你的昵称", "");

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
        // document.getElementById("msg").innerHTML = "<p>Connect to Service</p>";
        // document.getElementById("msg").innerHTML += '<p>连接到: '+_url+'</p>';
        // 发送登录消息
        webSocket.send(uname);
    };
    function onMessage(event){
        console.log("onMessage"+event.data);
        document.getElementById("msg").innerHTML += "<p>"+event.data+"</p>"
    };

    function onClose(event){
        document.getElementById("msg").innerHTML += "<p>断开连接，如要重新进入，请刷新界面</p>";
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
		uname = await websocket.recv()   # 等待获取用户名
		
		# 进入房间
		print(f'\n用户:{uname} 进入房间：{path}')   # 当前房间路径
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
					await conn.send(f'{uname}: {msg}')
			except websockets.ConnectionClosedOK:
				break
			except websockets.ConnectionClosedError:
				break
			print(f"recv: {msg}")
			
		self.conn[path].remove(websocket)  # 移除连接
		# 判断房间有没有人
		_conn = dict(self.conn)  # 复制一个副本
		for room in _conn:
			if len(_conn[room]) == 0:   # 房间没人了，销毁房间
				self.conn.pop(room)
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
		
