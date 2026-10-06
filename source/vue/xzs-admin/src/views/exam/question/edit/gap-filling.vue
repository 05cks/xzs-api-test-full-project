<template>
  <div class="app-container">
    <el-form :model="form" ref="form" label-width="100px" v-loading="formLoading" :rules="rules">
      <el-form-item label="年级：" prop="gradeLevel" required>
        <el-select v-model="form.gradeLevel" placeholder="年级" @change="levelChange">
          <el-option v-for="item in levelEnum" :key="item.key" :value="item.key" :label="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="学科：" prop="subjectId" required>
        <el-select v-model="form.subjectId" placeholder="学科">
          <el-option v-for="item in subjectFilter" :key="item.id" :value="item.id" :label="item.name+' ( '+item.levelName+' )'"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="题干：" prop="title" required>
        <el-input v-model="form.title" @focus="inputClick(form,'title')" />
      </el-form-item>
      <el-form-item label="填空答案：" required>
        <el-form-item :label="item.prefix" :key="item.prefix" v-for="item in form.items" label-width="50px" class="question-item-label">
          <el-input v-model="item.content" @focus="inputClick(item,'content')" class="question-item-content-input" style="width: 80%"/>
          <span class="question-item-span">分数：</span><el-input-number v-model="item.score" :precision="1" :step="1" :max="100"></el-input-number>
        </el-form-item>
      </el-form-item>
      <el-form-item label="解析：" prop="analyze" required>
        <el-input v-model="form.analyze" @focus="inputClick(form,'analyze')" />
      </el-form-item>
      <el-form-item label="分数：" prop="score" required>
        <el-input-number v-model="form.score" :precision="1" :step="1" :max="100"></el-input-number>
      </el-form-item>
      <el-form-item label="难度：" required>
        <el-rate v-model="form.difficult" class="question-item-rate"></el-rate>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button type="success" @click="showQuestion">预览</el-button>
      </el-form-item>
    </el-form>
    <el-dialog :visible.sync="richEditor.dialogVisible" append-to-body :close-on-click-modal="false" style="width: 100%;height: 100%" :show-close="false" center>
      <Ueditor @ready="editorReady"/>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="editorConfirm">确 定</el-button>
        <el-button @click="richEditor.dialogVisible = false">取 消</el-button>
      </span>
    </el-dialog>
    <el-dialog :visible.sync="questionShow.dialog" style="width: 100%;height: 100%">
      <QuestionShow :qType="questionShow.qType" :question="questionShow.question" :qLoading="questionShow.loading"/>
    </el-dialog>
  </div>
</template>

<script>
import QuestionShow from '../components/Show'
import Ueditor from '@/components/Ueditor'
import { mapGetters, mapState, mapActions } from 'vuex'
import questionApi from '@/api/question'

export default {
  components: {
    Ueditor, QuestionShow
  },
  data () {
    return {
      form: {
        id: null,
        questionType: 4,
        gradeLevel: null,
        subjectId: null,
        title: '',
        items: [
        ],
        analyze: '',
        correct: '',
        score: '',
        difficult: 0
      },
      subjectFilter: null,
      formLoading: false,
      rules: {
        gradeLevel: [
          { required: true, message: '请选择年级', trigger: 'change' }
        ],
        subjectId: [
          { required: true, message: '请选择学科', trigger: 'change' }
        ],
        title: [
          { required: true, message: '请输入题干', trigger: 'blur' }
        ],
        analyze: [
          { required: true, message: '请输入解析', trigger: 'blur' }
        ],
        score: [
          { required: true, message: '请输入分数', trigger: 'blur' }
        ]
      },
      richEditor: {
        dialogVisible: false,
        object: null,
        parameterName: '',
        instance: null
      },
      questionShow: {
        qType: 0,
        dialog: false,
        question: null,
        loading: false
      }
    }
  },
  created () {
    let id = this.$route.query.id
    let _this = this
    this.initSubject(function () {
      _this.subjectFilter = _this.subjects
    })
    if (id && parseInt(id) !== 0) {
      _this.formLoading = true
      questionApi.select(id).then(re => {
        _this.form = re.response
        _this.formLoading = false
      })
    }
  },
  methods: {
    editorReady (instance) {
      this.richEditor.instance = instance
      let currentContent = this.richEditor.object[this.richEditor.parameterName]
      this.richEditor.instance.setContent(currentContent)
      // 光标定位到Ueditor
      this.richEditor.instance.focus(true)
    },
    inputClick (object, parameterName) {
      this.richEditor.object = object
      this.richEditor.parameterName = parameterName
      this.richEditor.dialogVisible = true
    },
    editorConfirm () {
      let content = this.richEditor.instance.getContent()
      if (this.richEditor.parameterName === 'title') { // 题干的正确答案重置
        if (this.questionItemReset(content)) {
          this.richEditor.object[this.richEditor.parameterName] = content
          this.richEditor.dialogVisible = false
        } else {

        }
      } else {
        this.richEditor.object[this.richEditor.parameterName] = content
        this.richEditor.dialogVisible = false
      }
    },
    // 核心修改：适配 {_} 填空格式的识别和解析
    questionItemReset (content) {
      // 匹配 {_} 或 {_1}、{_2} 等格式（支持单空/多空）
      let spanRegex = new RegExp('\\{_(\\d*)\\}', 'g')
      let _this = this
      let newFormItem = []
      // 提取题干中所有填空标记
      let gapfillingItems = content.match(spanRegex)
      if (gapfillingItems === null) {
        this.$message.error('请插入填空（格式：{_} 或 {_1}）')
        return false
      }
      // 循环处理每个填空，生成答案输入框配置
      gapfillingItems.forEach(function (span, index) {
        let pairRegex = /\{_(\d*)\}/ // 提取填空序号（如无序号则用索引）
        pairRegex.test(span)
        let blankIndex = RegExp.$1 || (index + 1) // 填空序号（1、2、3...）
        newFormItem.push({
          id: null,
          itemUuid: `blank-${blankIndex}`, // 唯一标识（避免重复）
          prefix: `第${blankIndex}空`, // 答案输入框前的序号显示
          content: '', // 填空答案（初始为空）
          score: '0' // 每空分数（初始为0）
        })
      })
      // 保留已填写的答案（编辑时复用）
      newFormItem.forEach(function (item) {
        _this.form.items.some((oldItem, index) => {
          if (oldItem.itemUuid === item.itemUuid) {
            item.content = oldItem.content
            item.id = oldItem.id
            item.score = oldItem.score
            return true
          }
        })
      })
      // 更新表单中的填空配置（生成对应数量的答案输入框）
      _this.form.items = newFormItem
      return true
    },
    submitForm () {
      let _this = this
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.formLoading = true
          questionApi.edit(this.form).then(re => {
            if (re.code === 1) {
              _this.$message.success(re.message)
              _this.delCurrentView(_this).then(() => {
                _this.$router.push('/exam/question/list')
              })
            } else {
              _this.$message.error(re.message)
              this.formLoading = false
            }
          }).catch(e => {
            this.formLoading = false
          })
        } else {
          return false
        }
      })
    },
    levelChange () {
      this.form.subjectId = null
      this.subjectFilter = this.subjects.filter(data => data.level === this.form.gradeLevel)
    },
    showQuestion () {
      this.questionShow.dialog = true
      this.questionShow.qType = this.form.questionType
      this.questionShow.question = this.form
    },
    resetForm () {
      let lastId = this.form.id
      this.$refs['form'].resetFields()
      this.form = {
        id: null,
        questionType: 4,
        gradeLevel: null,
        subjectId: null,
        title: '',
        items: [
        ],
        analyze: '',
        correct: '',
        score: '',
        difficult: 0
      }
      this.form.id = lastId
    },
    ...mapActions('exam', { initSubject: 'initSubject' }),
    ...mapActions('tagsView', { delCurrentView: 'delCurrentView' })
  },
  computed: {
    ...mapGetters('enumItem', ['enumFormat']),
    ...mapState('enumItem', {
      questionTypeEnum: state => state.exam.question.typeEnum,
      levelEnum: state => state.user.levelEnum
    }),
    ...mapState('exam', { subjects: state => state.subjects })
  }
}
</script>