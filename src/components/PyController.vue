<template>
  <div>
    <!-- 使用 flex 布局的容器 -->
    <div>
      <!-- 使用 flex 布局的容器 -->
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>脚本参数设置</span>
        </div>
        <div style="display: flex; align-items: center;">
          <!-- 使用 flex-grow 属性来分配剩余空间 -->
          <el-radio style="margin-left: 200px;" v-model="radio" label=0>导入图片</el-radio>
          <span> 参数{{ isLogin }}</span>
          <!-- <span> 参数{{ token }}</span> -->
          <span> 参数{{ indexflag }}</span>

        </div>
      </el-card>
    </div>
    <div>
      <div>
        <el-popconfirm @confirm="clickRun" title="确认上传图片？">
          <el-button type="success" slot="reference" :loading="runDisabled">上传图片</el-button>
        </el-popconfirm>
        <el-popconfirm v-if="indexflag == 0" @confirm="clickUpload" title="确认上传erp图片？原图片会被覆盖" style="padding-left:20px ;">
          <el-button type="success" slot="reference" :loading="runDisabled">上传ERP图片</el-button>
        </el-popconfirm>
      </div>
      <el-divider></el-divider>
      <div class="my-class">
        <el-input style="color: #333;" type="textarea" :autosize="{ minRows: 20 }" placeholder="请输入内容"
          v-model="description" clearable>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script>
// const exec =  window.require('child_process').exec
const path = window.require('path');
const fs = window.require('fs');
import ajax from "@/assets/js/ajax";
import ConcurrencyLimiter from '@/assets/js/concurrencyLimiter';
import axios from 'axios';


export default {
  props: {
    isLogin: Number,
    token: String,// 修改了这里
    disr: String
  },
  data() {
    return {
      excelAddress: 'D：//示例文本.xlsx',
      imageAddress: 'D://',
      page: 0,
      description: '',
      folderPath: '', // 存放所选文件夹的路径
      drawer: false,
      illustrate: '文件使用说明',
      inputDesc: '参数说明',
      radio: '0',
      runDisabled: false,
      fileList: [],
      uploadResult: [],
      indexflag: 0
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
    async clickRun() {
      if (this.isLogin == 1) {
        //原始数据清除
        this.uploadResult = []
        //控制按钮为加载的样式，无法点击
        this.runDisabled = true
        this.description = ''
        //操作文件夹，将文件夹中的文件进行分类，并转为数据结构
        const files = fs.readdirSync(this.disr);
        const result = {} // 使用对象来存储目录和文件列表  

        files.forEach((file) => {
          const fullPath = path.join(this.disr, file);
          const stat = fs.statSync(fullPath);
          if (stat.isDirectory()) {
            // 如果是目录，递归调用并存储结果  
            const dirFiles = this.getFilesInDir(fullPath);
            if (!result[dirFiles.fileName]) {
              result[dirFiles.fileName] = [];
            }
            result[dirFiles.fileName].push(...dirFiles.fileList);
          } else {
            const extname = path.extname(file).toLowerCase();
            if (extname === '.jpg' || extname === '.png' || extname === '.jpeg') {
              this.indexflag++
              if (!result[path.basename(this.disr)]) {
                result[path.basename(this.disr)] = [];
              }

              result[path.basename(this.disr)].push(fullPath);
              console.log("文件开始传输")
            }
          }
        })
        // 处理每个子组（每组5个）
          for (const [dirName, itemArray] of Object.entries(result)) {
            if (!this.uploadResult[dirName]) {
              this.uploadResult[dirName] = new Array(itemArray.length);
            }
            //批处理大小（batchSize）
            const batchSize = 5;
            for (let i = 0; i < itemArray.length; i += batchSize) {
              const batch = itemArray.slice(i, i + batchSize);
              await Promise.all(batch.map((item, index) => this.imagePathToBlob(item, dirName, index)));
            }
          }
        console.log("全部执行完毕")
      } else {
        this.$notify.error({
          title: '错误',
          message: '未登录无法执行脚本，请登录后再试'
        });
      }
      this.runDisabled = false
    },


    // 本地图片转换为blob
    async imagePathToBlob(imagePath, dirName, index) {
      const data = await fs.promises.readFile(imagePath);
      const arrayBuffer = new Uint8Array(data).buffer;
      const blob = new Blob([arrayBuffer], { type: 'image/png' });
      await this.post(dirName, blob, index);
    },

    // 图片上传到阿里云
    async post(dirName, rawFile, index) {
      const options = {
        headers: {},
        withCredentials: false,
        file: rawFile,
        data: {},
        filename: "file",
        action: "https://ivr.yjwh.shop/aliyun/oss/upload/",
        onProgress: (e) => {
          // this.onProgress(e, rawFile);
          console.log(e)
        },
        onSuccess: async (res) => {
          let obj = {
            name: rawFile.name,
            webkitRelativePath: rawFile.webkitRelativePath,
            size: rawFile.size,
            type: rawFile.type,
            serialNumber: rawFile.serialNumber,
            file_name: rawFile.file_name,
          };
          let newObj = { ...obj, ...res.msg };
          this.description = this.description + "图片上传成功" + newObj.path + "/n"
          this.uploadResult[dirName][index] = newObj.path; // 使用索引插入网络地址
          this.indexflag--
          console.log(this.uploadResult)
        },
        onError: async (err) => {
          console.log(err)
          this.description = this.description + "图片上传失败" + err
          this.indexflag--

        },
      };
      const req = ajax(options);
      if (req && req.then) {
        req.then(options.onSuccess, options.onError);
      }
    },


    getFilesInDir(dir) {
      const files = fs.readdirSync(dir);
      const result = {}; // 使用对象来存储目录和文件列表  

      files.forEach((file) => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          // 如果是目录，递归调用并存储结果  
          const dirFiles = this.getFilesInDir(fullPath);
          // 使用目录名作为键，文件列表作为值  
          result[file] = dirFiles.fileList || [];
        } else {
          // 如果是文件，检查当前目录是否已在结果对象中  
          const extname = path.extname(file).toLowerCase();
          if (extname === '.jpg' || extname === '.png' || extname === '.jpeg') {
            this.indexflag++
            if (!result[path.basename(dir)]) {
              result[path.basename(dir)] = [];
            }
            // 将文件添加到当前目录的文件列表中  
            result[path.basename(dir)].push(fullPath);
          }
        }
      });

      // 返回包含目录和文件列表的对象  
      return { fileName: path.basename(dir), fileList: Object.values(result).flat() };
    },


    async uploadData(dirName, itemArray) {
      // 这里是上传数据的逻辑，返回一个Promise
      console.log(dirName);
      console.log(itemArray);

      // 假设使用了axios进行请求
      const postData = {
        goodsNo: dirName,
        imgList: itemArray
      };

      // 设置请求头部，包含token
      const config = {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      };
      if (this.isLogin == 1) {

        try {
          axios.defaults.baseURL = 'http://192.168.1.240:8063';
          const response = await axios.post('/api/goods/preSell/photoUploadByTool', postData, config)
          if (response.status === 200 || response.status === 201) {
            this.description = this.description + dirName + "图片上传成功"
            console.log(response.status);
          } else if (response.status === 400) {
            console.log("请求失败");
            this.description = this.description + dirName + "图片覆盖失败" + response.data.message
          } else {
            this.description = this.description + dirName + "发生未知错误，图片覆盖失败，请联系管理员"
          }
          return response.data;
        } catch (error) {
          console.error("上传数据时发生错误:", error);
          // 处理错误情况
          this.description = this.description + "发生未知错误，图片覆盖失败，请联系管理员"

        }
      } else {
        this.$notify.error({
          title: '错误',
          message: '未登录无法执行脚本，请登录后再试'
        });
      }
    },
    //上传erp接口
    clickUpload() {
      const limiter = new ConcurrencyLimiter(4); // 创建并发限制为4的limiter  
      this.processTasks(this.uploadResult, limiter)
    },

    processTasks(tasks, limiter) {
      console.log(ConcurrencyLimiter)
      for (const [dirName, itemArray] of Object.entries(tasks)) {
        // 为每个任务创建一个Promise，并通过limiter的 add 方法加入队列  
        limiter.add(() => this.uploadData(dirName, itemArray)).then(result => {
          console.log(`Task ${dirName} uploaded with result:`, result);
        }).catch(error => {
          console.error(`Failed to upload task ${dirName}`, error);
        });
      }

    },
  },
  watch: {
    disr() {
      console.log("监听方法--执行器" + this.disr)

    }
  },
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
</style>ajax(options)options.onSuccess
