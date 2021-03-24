<template>
  <div class="first">
    <el-container style="height: 500px">
    <el-aside style="width: 200px">
    <el-menu default-active="1" class="el-menu-vertical-demo" @select="moduleChange" :collapse=false>
      <el-menu-item index="1">
        <i class="el-icon-s-flag"></i>
        <span slot="title">代理</span>
      </el-menu-item>
      <el-menu-item index="2">
        <i class="el-icon-position"></i>
        <span slot="title">重放</span>
      </el-menu-item>
      <el-menu-item index="3">
        <i class="el-icon-s-order"></i>
        <span slot="title">历史</span>
      </el-menu-item>
      <el-menu-item index="4">
        <i class="el-icon-cpu"></i>
        <span slot="title">爆破</span>
      </el-menu-item>
    </el-menu>
    </el-aside>
    <el-container style="width:1000px">
      <Proxy v-if="state==0"/>
      <Repeater v-if="state==1"/>
      <History v-if="state==2"/>
      <Intruder v-if="state==3"/>
      <!-- <el-tab-pane v-show="state==1" label="重放">
        <el-tabs type="border-card">
          <el-tab-pane v-for="r in this.repeater" :key="r[1]" :label="r[1].toString()">{{r}}</el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane v-show="state==2" label="历史">
        <el-row v-for="h in this.history" :key="h[2]">{{h[0]+':'+h[1]}}</el-row>
      </el-tab-pane> -->
      </el-container>
    </el-container>
  </div>
</template>

<script>
// @ is an alias to /src
import Proxy from "@/components/Proxy.vue"
import Repeater from "@/components/Repeater.vue"
import History from "@/components/History.vue"
import Intruder from "@/components/Intruder.vue"
export default {
  name: "Home",
  components: {
    Repeater,
    Proxy,
    History,
    Intruder
  },
  methods: {
    moduleChange: function(index, indexPath) {
      this.state=index-1;
    }
  },
  data(){
    return {
      state: 0,
    }
  }
};

    Proxy</script>

<style>
.mytext .el-textarea__inner {
  font-family: Consolas, "Liberation Mono";
}
.el-row{
  margin-bottom: 20px;
}

</style>
