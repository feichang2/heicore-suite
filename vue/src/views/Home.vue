<template>
  <div class="home">
    <el-tabs type="border-card" @tab-click="moduleChange">
      <el-tab-pane v-show="state==0" label="代理">
        <el-tabs type="border-card" @tab-click="requestChange">
          <el-tab-pane label="Raw">
            <el-row>
              <el-input type="textarea" :rows="20" style="width:45%;" v-model="request" />
              <el-input type="textarea" :rows="20" style="width:45%;" v-model="response" />
            </el-row>
            <el-row>
              <el-switch v-model="isRequestScript" active-text="请求处理脚本"></el-switch>
              <el-switch v-model="isResponseScript" active-text="响应处理脚本"></el-switch>
            </el-row>
            <el-row>
              <el-input
                type="textarea"
                :rows="5"
                style="width:45%;"
                v-if="isRequestScript"
                v-model="request_script"
                placeholder="定义一个函数,接收一个字符串,返回一个字符串"
              />
              <el-input
                type="textarea"
                :rows="5"
                style="width:45%;"
                v-if="isResponseScript"
                v-model="response_script"
                placeholder="定义一个函数,接收一个字符串,返回一个字符串"
              />
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="Hex">
            <el-table :data="hexArray" style="width:100%;" :show-header="false">
              <el-table-column v-for="(item,key,index) in hexArray[0]" :key="key" :label="key">
                <template slot-scope="scope">
                  <el-input v-model="scope.row[scope.column.label]"></el-input>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
        <el-row v-show="state==0">
          <el-button type="primary" @click="setProxy">开启代理</el-button>
          <el-button type="primary" @click="forward">发送请求</el-button>
          <el-button type="primary" @click="drop">丢包</el-button>
          <el-button type="primary" @click="sendToClient">发送响应</el-button>
          <el-button type="primary" @click="stopProxy">停止代理</el-button>
          <el-button type="primary" @click="test">测试按钮</el-button>
        </el-row>
        <el-row v-show="state ==0">
          <el-button type="primary" @click="sendToRepeater">发给重发器</el-button>
        </el-row>
      </el-tab-pane>
      <el-tab-pane v-show="state==1" label="重放">
        <el-tabs type="border-card">
          <el-tab-pane v-for="r in this.repeater" :key="r[1]" :label="r[1].toString()">{{r}}</el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane v-show="state==2" label="历史">
        <el-row v-for="h in this.history" :key="h[2]">{{h[0]+':'+h[1]}}</el-row>
      </el-tab-pane>
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
        var response = await eel.queryData(this.filter)();
        console.log("query once");
        if (response && !response[1]) {
          //not filtered and not null
          this.buf = response[0];
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
        } else if (response && response[1]) {
          //filtered
          this.history.push([
            response[0],
            await eel.sendDataToServer(response[0])(),
            this.history_index++
          ]);
        }
      }
    },
    forward: async function() {
      console.log("send to server");
      this.request = "";
      if (this.isRequestScript) {
        this.request = await eel.processData(
          this.request,
          this.request_script
        )();
      }
      this.response = await eel.sendDataToServer(this.request, 0)();
    },
    sendToClient: async function() {
      if (this.isResponseScript) {
        this.response = await eel.processData(
          this.response,
          this.response_script
        )();
      }
      eel.sendDataToClient(
        this.response
      );
      this.history.push([this.request, this.response, this.history_index++]);
      this.request = "";
      this.response = "";
      this.update_request_data = true;
      this.query_task = setInterval(this.queryData, 1000);
      console.log("send to client");
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
    moduleChange: function(tab, event) {
      if ((tab.$props.label == "代理")) {
        this.state = 0;
      } else if ((tab.$props.label == "重放")) {
        this.state = 1;
      } else if ((tab.$props.label == "历史")) {
        this.state = 2;
      }
    },
    requestChange: function(tab, event) {
      if (tab.$props.label == "Hex") {
        this.rawToHex();
      } else if (tab.$props.label == "Raw") {
        this.hexToRaw();
      }
    },
    rawToHex: function() {
      this.hex = "";
      this.hexArray = [];
      var a = {
        0: "",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: "",
        9: ""
      };
      for (var i = 0; i < this.request.length || i % 10 != 0; i++) {
        if (i < this.request.length)
          var s = this.request.charCodeAt(i).toString(16);
        else var s = "00";
        if (s.length != 2) {
          s = "0" + s;
        }
        this.hex += s + " ";
        a[i % 10] = s;
        if (i % 10 == 9) {
          this.hexArray.push(a);
          var a = {
            0: "",
            1: "",
            2: "",
            3: "",
            4: "",
            5: "",
            6: "",
            7: "",
            8: "",
            9: ""
          };
        }
      }
      this.hex = this.hex.substring(0, this.hex.length - 1);
    },
    hexToRaw: function() {
      this.request = "";
      console.log(this.request);
      for (var i = 0; i < this.hexArray.length - 1; i++) {
        for (var j = 0; j < 10; j++)
          this.request += String.fromCharCode(
            parseInt(this.hexArray[i][j], 16)
          );
      }
      var len = this.hexArray.length - 1;
      var s = "";
      for (var j = 9; j >= 0; j--)
        if (this.hexArray[len][j] != "00")
          s += String.fromCharCode(parseInt(this.hexArray[len][j], 16));
      this.request += s
        .split("")
        .reverse()
        .join("");
    },
    sendToRepeater: function() {
      this.repeater.push([this.request, this.repeater_index++]);
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
      raw: 0,
      filter: "css||js", //正则匹配的参数,'||'分割,交给python
      request_script: "",
      response_script: "",
      isRequestScript: false,
      isResponseScript: false,
      history: [],
      repeater: [],
      repeater_index: 0,
      history_index: 0,
      hexArray: []
    };
  },
  computed: {}
};
</script>

<style scoped>
</style>
