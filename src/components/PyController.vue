<template>
  <div>
    <!-- 使用 flex 布局的容器 -->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>通用设置</span>
      </div>
      <div style="display: flex; align-items: center;">
        <!-- 使用 flex-grow 属性来分配剩余空间 -->
        <span style="width: 150px;">图片文件夹下载地址</span>

        <el-input placeholder="请输入内容" v-model="imageAddress" clearable style="width: 250px;"></el-input>
        <div>
          <el-button type="primary" @click="selectDirectory">选择文件夹</el-button>
          <input type="file" id="file-selector" style="display: none" webkitdirectory @change="handleFiles"
            ref="fileSelector">

        </div>


        <span style="width: 150px; margin-left: 10px;">Excel下载地址</span>
        <el-input placeholder="请输入内容" v-model="excelAddress" clearable style="width: 250px;"></el-input>
      </div>
    </el-card>

    <div>
      <!-- 使用 flex 布局的容器 -->
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>脚本参数设置</span>
        </div>
        <div style="display: flex; align-items: center;">
          <!-- 使用 flex-grow 属性来分配剩余空间 -->
          <span style="width: 150px;">拍卖会ID</span>
          <el-input placeholder="请输入内容" v-model="catUrl" clearable style="width: 250px;"></el-input>
          <el-radio style="margin-left: 200px;" v-model="radio" label=0>导出文本和图片</el-radio>
          <el-radio v-model="radio" label=1>仅导出文本</el-radio>
          <span> 参数{{ message }}</span>
          <span> 参数{{ token }}</span>

        </div>
      </el-card>
    </div>
    <div>
    <div class="my-class">
      <el-input style="color: #333;" type="textarea" :autosize="{ minRows: 20 }" placeholder="请输入内容" v-model="description"
        clearable>
      </el-input>
    </div>
  </div>
</div></template>

<script>
// const exec =  window.require('child_process').exec
const path = window.require('path');
var iconv = require('iconv-lite');
const { spawn } = window.require('child_process');


export default {
  props: {
    message: Number,
    token: String // 修改了这里
  },
  data() {
    return {
      excelAddress: 'D：//示例文本.xlsx',
      imageAddress: 'D://',
      catUrl: 'www.baidu.com',
      page: 0,
      description: '',
      folderPath: '', // 存放所选文件夹的路径
      drawer: false,
      illustrate: '文件使用说明',
      inputDesc: '参数说明',
      radio: '0',
      runDisabled: false,
    };
  },
  mounted() { },
  methods: {

    selectDirectory() {
      this.$refs.fileSelector.click();
    },

    //选择文件夹
    handleFiles(event) {
      const filePath = event.target.files[0].path;
      this.folderPath = path.dirname(filePath);
      console.log(this.folderPath)
      this.imageAddress = this.folderPath
    },

    //点击事件
    clickRun() {
      let t = this
      //控制按钮为加载的样式，无法点击
      this.runDisabled = true
      console.log(this.runDisabled)
      //清除之前的控制台缓存
      t.description = ''
      this.cmdCopy(this.excelAddress, this.imageAddress, this.catUrl, this.page,this.radio, function (e) {
        // t.description = e // 这里直接赋值可能不会更新视图
        t.description = t.description + iconv.decode(e, 'GBK')
        console.log("打印--", t.description)

      })
    },

    //运行python脚本
    cmdCopy(excelAddress, imageAddress, catUrl, page,radio, callbackFun) {
      //开关控制
      try {
        console.log(path.resolve(this.message))
        // 任何你期望执行的 cmd 命令，ipconfig 为例
        // const cmd = 'ping www.baidu.com ';
        const cmd = `python -u ${path.resolve(this.message)} ${catUrl} ${excelAddress} ${imageAddress} ${page} ${radio}`
        // const cmd = 'python -u E://测试/testPy.py ';
        console.log("cmd" + cmd)
        //运行python命令

        // 创建一个子进程，设置 shell 和 encoding 选项
        const child = spawn(cmd, { shell: true, encoding: 'buffer' });
        // 监听子进程的标准输出流
        child.stdout.on('data', (data) => {
          // 使用 iconv-lite 解码 Buffer 对象
          console.log(iconv.decode(data, 'GBK'));
          // 使用 callbackFun 函数或其他方式处理输出结果
          callbackFun(data);
        });

        // 监听子进程的标准错误流
        child.stderr.on('data', (data) => {
          // 使用 iconv-lite 解码 Buffer 对象
          console.error(iconv.decode(data, 'GBK'));
          // 使用 callbackFun 函数或其他方式处理输出结果
          callbackFun(data);
        });

        //监听关闭流
        child.on('close', (data) => {
          console.log(iconv.decode(data, 'GBK'));
          this.runDisabled = false 
        });
      } catch (e) {
        console.log(e)
      }
    },

    //python文件参数说明
    illustrateShow() {
      this.drawer = true
      this.inputDesc = "图片文件夹下载地址：图片保存的路径 <br> Excel下载地址:拍品文本的下载地址，需要具体到文件名称 如D：//示例文本.xlsx <br> 网页地址: 需要抓取的网址 <br> "
      if (this.message.includes("drouot")) {
        this.illustrate = `本脚本抓取的是www.drouot.com网址专用的脚本 抓取的网址获取方式为：<br>
        1.打开要抓取的网页（必须是drouot网站）<br>
        2.负责上方网页链接填入抓取地址 <br>
        3.在起始页码处填写0  <br>
        4.执行脚本 <br>
        `
      }
    }
  } 
}


</script>



<style>
.text {
  font-size: 14px;
}

.item {
  margin-bottom: 0px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}

.box-card {
  width: 600;
}

/* 修改文本域的边框颜色和圆角 */
.my-class ::v-deep .el-textarea__inner {
  border: 1px solid #3d66e4;
  border-radius: 4px;
  color: #333;
}
</style>
