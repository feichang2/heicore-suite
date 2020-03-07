<template>
  <div class="home">
    <div>
      <Page msg="proxy" :activate="new_data_coming" />
    </div>
    <div v-show="state==0">
      <textarea v-model="request" />
      <textarea v-model="response" />
      <button type="button" @click="setProxy">set proxy</button>
      <button type='button' @click="forward">forward</button>
      <button @click="stopProxy">stop</button>
      <button @click='test'>test</button>
    </div>
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
    queryData: function() {
      if (this.update_request_data) {
        eel.queryData()(val => {
          this.buf = val;
        });
        console.log('query once')
        if (this.buf) {
          this.request = this.buf;
          this.update_request_data = false;
          this.new_data_coming = true;
          clearInterval(this.query_task);
          this.query_task = 0;
        }
      }
    },
    forward: function() {
      console.log("send to server");
      eel.sendDataToServer(this.request)(val => {
        this.response = val;
      });
      console.log("send to client");
      eel.sendDataToClient(this.response);
      this.query_task = setInterval(this.query_task, 1000);
    },
    stopProxy: function() {
      if (this.query_task) clearInterval(this.query_task);
      eel.endListening();
    },
    test: function(){
      eel.hello_world()(val =>{
        this.response=val
      })
    }
  },
  data() {
    return {
      state: 0,
      request: "",
      response: "",
      buf: "",
      update_request_data: false,
      query_task: 0,
      new_data_coming: false
    };
  }
};
</script>
