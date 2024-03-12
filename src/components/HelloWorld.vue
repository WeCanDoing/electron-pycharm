<template>
    <div class="hello">
        <el-container style="height: 1000px; border: 1px solid #eee">
            <el-aside width="400px" style="background-color:#fdfdfd">
                <div style="height: 60px; background-color: #B3C0D1;"></div>
                <div style="width: 380px;">
                    <file-list v-on:my-event="handleEvent" :disr="disr"></file-list>
                    <button @click="selectDirectory">选择文件夹</button>  
                     <p>选择的文件夹路径: {{ folderPath }}</p>  
                    <input type="file" id="file-selector" style="display: none" webkitdirectory @change="handleFiles"
                        ref="fileSelector">
                </div>
            </el-aside>
            <el-container>
                <el-header style=" font-size: 20px,">
                    <div v-if="isLogin == 0" style="margin-top: 10px;">
                        <span style="width: 150px; padding-right: 10px;">用户名</span>
                        <el-input placeholder="请输入内容" v-model="userName" clearable style="width: 250px;"></el-input>
                        <span style="width: 150px; margin-left: 10px;padding-right: 10px;">密码</span>
                        <el-input placeholder="请输入内容" v-model="passworld" clearable
                            style="width: 250px; margin-right: 10px;" show-password></el-input>
                        <el-button type="success" icon="el-icon-user" round @click="login">登录</el-button>
                    </div>
                    <div v-if="isLogin == 1" tyle="margin-top: 10px;ont-size: 26px;">
                        {{ username }}
                    </div>
                </el-header>
                <el-main>
                    <py-controller :message="isLogin" :token ="token"></py-controller>
                </el-main>
            </el-container>
        </el-container>

    </div>
</template>

<script>
import PyController from './PyController.vue';
import FileList from './FileList.vue';
import { encrypt } from '@/utils/rsaEncrypt'
import axios from 'axios';
const path = window.require('path');

export default {
    name: 'HelloWorld',
    components: {
        FileList,
        PyController
    },

    data() {

        return {
            username: "管理员",
            isLogin: 0,
            dialogVisible: false,
            userName: "admin",
            passworld: "123456",
            token: "admin",
            disr: 'C://Users/Administrator/Pictures/测试',
            folderPath:''
        }

  },
    methods: { 
    
        selectDirectory() {
            this.$refs.fileSelector.click();
        },
        handleFiles(event) {
            const filePath = event.target.files[0].path;
            this.folderPath = path.dirname(filePath);
            this.disr = this.folderPath
            console.log(this.folderPath)
        },
        handleEvent(data) {
            // data 是子组件传递过来的参数，获取路径
            console.log("地址", data)
            this.disr = data
        },

        // 登录方法
        login() {
            {
                const postData = {
                    userName: this.userName,
                    password: encrypt(this.passworld)
                };
                axios.post('/api/admin/auth/login', postData).then(response => {
                    if (response.status === 200) {
                        console.log(response.status);
                        this.token = response.data.token;
                        this.isLogin = 1
                    } else {
                        console.log("请求失败")
                    }

                })
                    .catch(error => {
                        console.error('请求失败:', error);
                    });
            }
        }

    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
    margin: 40px 0 0;
}

ul {
    list-style-type: none;
    padding: 0;
}

li {
    display: inline-block;
    margin: 0 10px;
}

a {
    color: #42b983;
}

.el-header {
    background-color: #B3C0D1;
    color: #333;
}

.el-aside {
    color: #333;
}
</style>
