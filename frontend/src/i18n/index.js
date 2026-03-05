import { createI18n } from 'vue-i18n'
import en from './en.js'
import zh from './zh.js'

const messages = {
  en,
  zh
}

const locale = localStorage.getItem('locale') || 'zh'

const i18n = createI18n({
  legacy: false, // you must set `false`, to use Composition API
  locale: locale, // set locale
  fallbackLocale: 'zh', // set fallback locale
  messages, // set locale messages
})

export default i18n
