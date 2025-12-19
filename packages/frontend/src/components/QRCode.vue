<template>
  <canvas ref="canvas"></canvas>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import QRCode from 'qrcode'

const props = defineProps<{
  value: string
  size?: number
}>()

const canvas = ref<HTMLCanvasElement>()

const generateQRCode = async () => {
  if (!canvas.value || !props.value) return
  
  try {
    await QRCode.toCanvas(canvas.value, props.value, {
      width: props.size || 200,
      margin: 1,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
  } catch (error) {
  }
}

watch(() => props.value, generateQRCode)
watch(() => props.size, generateQRCode)

onMounted(generateQRCode)
</script>
