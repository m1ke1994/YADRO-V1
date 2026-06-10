<script setup>
import { computed, onMounted, ref } from 'vue'
import { Image, Search, Trash2, X } from '@lucide/vue'

import { deleteMediaFile, listMediaFiles, updateMediaFile } from '../api/media'
import { BACKEND_URL } from '../config/env'

const props = defineProps({
  siteId: {
    type: [Number, String],
    required: true,
  },
  mediaType: {
    type: String,
    default: 'image',
  },
})

const emit = defineEmits(['close', 'select', 'deleted'])
const items = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')
const editingId = ref(null)
const metadata = ref({ title: '', alt_text: '' })

const emptyMessage = computed(() =>
  search.value ? 'По вашему запросу ничего не найдено.' : 'В библиотеке пока нет файлов.',
)

function previewUrl(item) {
  const value = item?.path || item?.url || ''
  if (/^https?:\/\//i.test(value)) return value
  return `${BACKEND_URL}${value.startsWith('/') ? value : `/${value}`}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    items.value = await listMediaFiles({
      site: props.siteId,
      fileType: props.mediaType,
      search: search.value.trim(),
    })
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || 'Не удалось загрузить медиатеку.'
  } finally {
    loading.value = false
  }
}

function selectItem(item) {
  emit('select', item)
}

function startEditing(item) {
  editingId.value = item.id
  metadata.value = {
    title: item.title || '',
    alt_text: item.alt_text || item.alt || '',
  }
}

async function saveMetadata(item) {
  error.value = ''
  try {
    const updated = await updateMediaFile(item.id, metadata.value)
    items.value = items.value.map((entry) => (entry.id === item.id ? updated : entry))
    editingId.value = null
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || 'Не удалось сохранить описание файла.'
  }
}

async function removeItem(item) {
  if (!window.confirm(`Удалить файл «${item.original_name || item.filename}» из медиатеки?`)) return

  error.value = ''
  try {
    await deleteMediaFile(item.id)
    items.value = items.value.filter((entry) => entry.id !== item.id)
    emit('deleted', item)
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || 'Не удалось удалить файл.'
  }
}

onMounted(load)
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4" @click.self="emit('close')">
    <section class="flex max-h-[88vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl">
      <header class="flex items-center justify-between border-b border-slate-200 px-4 py-3 sm:px-5">
        <div>
          <h2 class="text-lg font-semibold text-slate-950">Медиатека</h2>
          <p class="text-sm text-slate-500">Выберите существующий файл или управляйте его описанием.</p>
        </div>
        <button type="button" class="icon-button" aria-label="Закрыть" @click="emit('close')">
          <X :size="19" />
        </button>
      </header>

      <div class="flex gap-2 border-b border-slate-200 p-4">
        <div class="relative flex-1">
          <Search class="pointer-events-none absolute left-3 top-3 text-slate-400" :size="17" />
          <input
            v-model="search"
            class="form-control pl-9"
            placeholder="Название или alt-текст"
            @keyup.enter="load"
          >
        </div>
        <button type="button" class="action-button-secondary" :disabled="loading" @click="load">
          Найти
        </button>
      </div>

      <p v-if="error" class="notice-error m-4">{{ error }}</p>
      <div v-if="loading" class="empty-state m-4">
        <span class="loading-dot" />
        <p>Загружаем медиатеку...</p>
      </div>
      <div v-else-if="!items.length" class="empty-state m-4">
        <Image :size="28" />
        <p>{{ emptyMessage }}</p>
      </div>
      <div v-else class="grid overflow-y-auto p-4 sm:grid-cols-2 lg:grid-cols-3">
        <article v-for="item in items" :key="item.id" class="m-1 rounded-lg border border-slate-200 p-3">
          <button type="button" class="block w-full text-left" @click="selectItem(item)">
            <div class="aspect-video overflow-hidden rounded-lg bg-slate-100">
              <img
                v-if="item.file_type === 'image'"
                :src="previewUrl(item)"
                :alt="item.alt_text || item.title || item.filename"
                class="h-full w-full object-cover"
              >
              <video v-else :src="previewUrl(item)" class="h-full w-full object-cover" muted />
            </div>
            <p class="mt-2 truncate text-sm font-medium text-slate-900">{{ item.title || item.filename }}</p>
            <p class="truncate text-xs text-slate-500">{{ item.original_name }}</p>
          </button>

          <div v-if="editingId === item.id" class="mt-3 space-y-2">
            <input v-model="metadata.title" class="form-control" placeholder="Название">
            <input v-model="metadata.alt_text" class="form-control" placeholder="Alt-текст">
            <div class="flex gap-2">
              <button type="button" class="action-button-primary" @click="saveMetadata(item)">Сохранить</button>
              <button type="button" class="action-button-secondary" @click="editingId = null">Отмена</button>
            </div>
          </div>
          <div v-else class="mt-3 flex justify-between gap-2">
            <button type="button" class="text-xs font-medium text-cyan-800" @click="startEditing(item)">
              Изменить описание
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1 text-xs font-medium text-rose-600"
              @click="removeItem(item)"
            >
              <Trash2 :size="14" /> Удалить
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
