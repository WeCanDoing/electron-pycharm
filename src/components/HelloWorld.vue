<template>
  <!-- 使用示例 -->
  <div class="live2d">
    <!-- 可尝试一个页面上多个模型： -->
    <!-- <live2d
      :model="[1, 53]"
      :direction="direction"
      :width="width"
      :height="height"
      customId="vue-live2d-mian-2"
    ></live2d> -->
    <live2d
      :style="style"
      :model="['Potion-Maker/Pio', 'school-2017-costume-yellow']"
      :direction="direction"
      :size="size"
    ></live2d>
  </div>
</template>

<script>
/*
 * 项目中引用包时，将 import 内容替换
 * import live2d from 'vue-live2d'
 */
import live2d from 'vue-live2d'

export default {
  name: 'App',
  components: {
    live2d
  },
  data () {
    return {
      direction: 'right',
      style: 'position: fixed; top: calc(50% - 250px); left: calc(50% - 200px)',
      width: 300,
      height: 300,
      size: 350,
      tips: {
        mouseover: [{
          selector: '.vue-live2d',
          texts: ['这样可以修改默认语句']
        }]
      }
    }
  },
  created () {
    // tips 未使用，可自行在组件绑定此参数，注意此参数只会初始化一次
    this.tips = this.customTips
  }
}
</script>

<style>
body {
  margin: 20px;
  padding: 0;
  -webkit-app-region: drag;
}

</style>