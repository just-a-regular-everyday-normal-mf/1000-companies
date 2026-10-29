// Zero-dependency server: serves index.html and stores data in data.json
const http=require('http'),fs=require('fs'),path=require('path');
const PORT=process.env.PORT||3000,DATA=path.join(__dirname,'data.json');
if(!fs.existsSync(DATA))fs.writeFileSync(DATA,'[]');
http.createServer((req,res)=>{
 if(req.url.startsWith('/api/apps')){
  if(req.method==='GET'){res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');return res.end(fs.readFileSync(DATA))}
  if(req.method==='PUT'){let b='';req.on('data',c=>b+=c);req.on('end',()=>{
   try{JSON.parse(b);fs.writeFileSync(DATA+'.tmp',b);fs.renameSync(DATA+'.tmp',DATA);res.end('ok')}
   catch(e){res.statusCode=400;res.end('bad json')}});return}
 }
 res.setHeader('Content-Type','text/html');res.end(fs.readFileSync(path.join(__dirname,'index.html')));
}).listen(PORT,()=>console.log('Running on http://localhost:'+PORT));
