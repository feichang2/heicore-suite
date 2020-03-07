<template>
<div>
  <input type="text" v-model="inputValue" />
  <button @click="onClick">Send</button>
  <div>
  {{ response }}
  </div>
</div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data: function() {
    return {
      message: "",
      inputValue: "",
      response: ""
    }
  },
  methods: {
    onClick() {
    // Passing string to Python.
    eel.print_string(this.inputValue)((val) => {
      // Return response from Python.
      this.response = val
    })
    }
  }
}
</script>
