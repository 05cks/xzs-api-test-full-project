<template>
  <div style="line-height:1.8">
    <div v-if="qType==1" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
      <div class="q-content">
          <span :key="item.id" v-for="item in question.items" class="q-item-contain">
            <span class="q-item-prefix">{{item.prefix}}</span>
            <span v-html="item.content" class="q-item-content"></span>
          </span>
      </div>
    </div>
    <div v-else-if="qType==2" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
      <div class="q-content">
          <span :key="item.id" v-for="item in question.items" class="q-item-contain">
            <span class="q-item-prefix">{{item.prefix}}</span>
            <span v-html="item.content" class="q-item-content"></span>
          </span>
      </div>
    </div>
    <div v-else-if="qType==3" v-loading="qLoading">
  <!-- 题干 -->
  <div class="q-title" v-html="question.title" style="display: inline;margin-right: 10px;"/>
  <!-- 填空下划线（循环渲染多个填空，适配多空题） -->
  <span :key="item.id" v-for="item in question.items" style="margin: 0 8px;">
    <!-- 下划线样式：可根据需求调整高度、颜色 -->
    <span class="fill-blank" 
          :style="{ width: item.blankWidth || '80px' }">
    </span>
    <!-- 若需要显示填空序号（如 ①、②），可添加： -->
    <span class="blank-index" style="margin-left: 4px;">{{ item.prefix || '' }}</span>
  </span>
  </div>
    <div v-else-if="qType==4" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
    </div>
    <div v-else-if="qType==5" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
    </div>
    <div v-else>
    </div>
  </div>

</template>


<script>
export default {
  name: 'QuestionShow',
  props: {
    question: {
      type: Object,
      default: function () {
        return {}
      }
    },
    qLoading: {
      type: Boolean,
      default: false
    },
    qType: {
      type: Number,
      default: 0
    }
  },
  methods: {}
}
</script>
<template>
  <div style="line-height:1.8">
    <div v-if="qType==1" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
      <div class="q-content">
          <span :key="item.id" v-for="item in question.items" class="q-item-contain">
            <span class="q-item-prefix">{{item.prefix}}</span>
            <span v-html="item.content" class="q-item-content"></span>
          </span>
      </div>
    </div>
    <div v-else-if="qType==2" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
      <div class="q-content">
          <span :key="item.id" v-for="item in question.items" class="q-item-contain">
            <span class="q-item-prefix">{{item.prefix}}</span>
            <span v-html="item.content" class="q-item-content"></span>
          </span>
      </div>
    </div>
    <div v-else-if="qType==3" v-loading="qLoading">
  <!-- 题干 -->
  <div class="q-title" v-html="question.title" style="display: inline;margin-right: 10px;"/>
  <!-- 填空下划线（循环渲染多个填空，适配多空题） -->
  <span :key="item.id" v-for="item in question.items" style="margin: 0 8px;">
    <!-- 下划线样式：可根据需求调整高度、颜色 -->
    <span class="fill-blank" 
          :style="{ width: item.blankWidth || '80px' }">
    </span>
    <!-- 若需要显示填空序号（如 ①、②），可添加： -->
    <span class="blank-index" style="margin-left: 4px;">{{ item.prefix || '' }}</span>
  </span>
  </div>
    <div v-else-if="qType==4" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
    </div>
    <div v-else-if="qType==5" v-loading="qLoading">
      <div class="q-title" v-html="question.title"/>
    </div>
    <div v-else>
    </div>
  </div>

</template>

<script>
export default {
  name: 'QuestionShow',
  props: {
    question: {
      type: Object,
      default: function () {
        return {}
      }
    },
    qLoading: {
      type: Boolean,
      default: false
    },
    qType: {
      type: Number,
      default: 0
    }
  },
  methods: {}
}
</script>
<style scoped>
/* 填空题下划线样式 */
.fill-blank {
  display: inline-block;
  height: 2px;
  background-color: #333;
  vertical-align: middle;
}
/* 填空序号样式 */
.blank-index {
  font-size: 14px;
  color: #666;
  margin-left: 4px;
}
/* 题干样式 */
.q-title {
  font-weight: 500;
  font-size: 16px;
}
/* 补充原有题型的样式（保持一致性） */
.q-content {
  margin-top: 8px;
}
.q-item-contain {
  display: block;
  margin: 6px 0;
}
.q-item-prefix {
  display: inline-block;
  width: 24px;
  text-align: center;
  margin-right: 8px;
}
.q-item-content {
  vertical-align: middle;
}
</style>

