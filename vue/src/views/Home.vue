<template>
  <div class="home">
    <el-tabs type="border-card">
      <el-tab-pane v-show="state==0" label="代理">
        <el-tabs type="border-card" @tab-click="requestChange">
          <el-tab-pane label="Raw">
            <el-input
              type="textarea"
              :rows="20"
              style="width:45%;"
              v-model="request"
            />
          </el-tab-pane>
          <el-tab-pane label="Hex" @tab-click="rawToHex">
            <el-input
              type="textarea"
              :rows="20"
              style="width:45%;"
              v-model="hex"
              @change="hexToRaw"
            />
          </el-tab-pane>
        </el-tabs>
        <el-row v-show="state==0">
          <el-button type="primary" @click="setProxy">开启代理</el-button>
          <el-button type="primary" @click="forward">放包</el-button>
          <el-button type="primary" @click="drop">丢包</el-button>
          <el-button type="primary" @click="stopProxy">停止代理</el-button>
          <el-button type="primary" @click="test">测试按钮</el-button>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="重放"></el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
// @ is an alias to /src
import Page from "@/components/Page.vue";

export default {
  name: "Home",
  components: {
    Page
  },
  methods: {
    setProxy: function() {
      eel.beginListening();
      this.query_task = setInterval(this.queryData, 1000);
      this.update_request_data = true;
    },
    queryData: async function() {
      if (this.update_request_data) {
        this.buf = await eel.queryData(this.filter)();
        console.log("query once");
        if (this.buf) {
          this.request = this.buf.replace("keep-alive", "close");
          this.update_request_data = false;
          if (this.state != 0) {
            this.$notify({
              title: "一个新的包被捕获",
              dangerouslyUserHTMLString: true,
              message:
                "" +
                this.request
                  .split("\n")
                  .slice(0, 3)
                  .join("\n")
            });
          }
          clearInterval(this.query_task);
          this.query_task = 0;
        }
      }
    },
    forward: async function() {
      console.log("send to server");
      this.request_history.push(this.request);
      this.request = "";
      this.update_request_data = true;
      this.query_task = setInterval(this.queryData, 1000);
      this.response = await eel.sendDataToServer(
        this.request_history[this.request_history.length - 1],
        1
      )();
      console.log("send to client");
      this.response_history.push(this.response);
      this.response = "";
    },
    stopProxy: function() {
      if (this.query_task) clearInterval(this.query_task);
      eel.endListening();
    },
    test: function() {
      this.$notify({
        title: "一个新的包被捕获",
        dangerouslyUseHTMLString: true,
        message:
          "<strong>" +
          this.request
            .split("\n")
            .slice(0, 3)
            .join("<br>") +
          "</strong>"
      });
    },
    drop: function() {
      eel.drop()();
      this.request = "";
    },
    requestChange:function(tab,event){
      if(tab.$props.label=="Hex"){
        this.rawToHex();
      }
    },
    rawToHex: function() {
      this.hex = "";
      for (var i = 0; i < this.request.length; i++) {
        var s=this.request.charCodeAt(i).toString(16)
        if(s.length!=2){
          s='0'+s
        }
        this.hex += s + " ";
      }
      this.hex = this.hex.substring(0, this.hex.length - 1);
    },
    hexToRaw: function() {
      this.request = "";
      var list = this.hex.split(" ");
      for (var i = 0; i < list.length; i++) {
        this.request += String.fromCharCode(parseInt(list[i], 16));
      }
    }
  },
  data() {
    return {
      state: 0,
      request: "",
      hex: "",
      param: {},
      response: "",
      buf: "",
      update_request_data: false,
      query_task: 0,
      request_history: [],
      response_history: [],
      raw: 0,
      filter:"css|js"//正则匹配的参数,'|'分割,交给python
    };
  }
};
</script>

<style scoped>
</style>
