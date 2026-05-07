---
name: healthcheck
description: "使用 JSON 文件存储来追踪饮水量和睡眠记录。"
---

# 健康追踪器

使用 JSON 文件简单追踪饮水和睡眠。

## 数据格式

文件：`{baseDir}/health-data.json`

```json
{
  "water": [{"time": "ISO8601", "cups": 2}],
  "sleep": [{"time": "ISO8601", "action": "sleep|wake"}]
}
```

## 添加饮水记录

当用户说"喝了 X 杯"或类似内容时：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d={water:[],sleep:[]};try{d=JSON.parse(fs.readFileSync(f))}catch(e){}d.water.push({time:new Date().toISOString(),cups:CUPS});fs.writeFileSync(f,JSON.stringify(d));console.log('已记录: '+CUPS+' 杯')"
```

将 `CUPS` 替换为用户输入的数字。

## 添加睡眠记录

当用户说"要去睡觉"时：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d={water:[],sleep:[]};try{d=JSON.parse(fs.readFileSync(f))}catch(e){}d.sleep.push({time:new Date().toISOString(),action:'sleep'});fs.writeFileSync(f,JSON.stringify(d));console.log('已记录: 睡眠')"
```

## 添加醒来记录

当用户说"醒了"时：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d={water:[],sleep:[]};try{d=JSON.parse(fs.readFileSync(f))}catch(e){}const last=d.sleep.filter(s=>s.action==='sleep').pop();d.sleep.push({time:new Date().toISOString(),action:'wake'});fs.writeFileSync(f,JSON.stringify(d));if(last){const h=((new Date()-new Date(last.time))/3600000).toFixed(1);console.log('睡了: '+h+' 小时')}else{console.log('已记录: 醒来')}"
```

## 查看统计

当用户询问统计时：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d={water:[],sleep:[]};try{d=JSON.parse(fs.readFileSync(f))}catch(e){}console.log('饮水:',d.water.length,'条记录');console.log('睡眠:',d.sleep.length,'条记录');const today=d.water.filter(w=>new Date(w.time).toDateString()===new Date().toDateString());console.log('今天:',today.reduce((s,w)=>s+w.cups,0),'杯')"
```

## 更新记录

更新最后一条饮水记录：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d=JSON.parse(fs.readFileSync(f));d.water[d.water.length-1].cups=NEW_CUPS;fs.writeFileSync(f,JSON.stringify(d));console.log('已更新')"
```

## 删除记录

删除最后一条饮水记录：

```bash
node -e "const fs=require('fs');const f='{baseDir}/health-data.json';let d=JSON.parse(fs.readFileSync(f));d.water.pop();fs.writeFileSync(f,JSON.stringify(d));console.log('已删除')"
```

## 注意

- 仅使用 Node.js 内置模块
- 文件缺失时自动创建
- 所有时间戳为 ISO8601 格式
