<template>
  <div class='page' :style="{backgroudColor:activate?'red':'white'}">
{{msg}}
  </div>
</template>

<script>
export default {
  data () {
    return {

    }
  },
  methods: {

  },
  props:{
msg:{
    type: String,
    required:true
},
activate:{
    type:Boolean
}
  }
}
</script>

<style scoped>
.page{
    display: inline-block;
}
</style>
