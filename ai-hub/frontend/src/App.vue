<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <ErrorBoundary>
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </ErrorBoundary>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import ErrorBoundary from '@/shared/components/common/ErrorBoundary.vue'
import type { GlobalThemeOverrides } from 'naive-ui'

/** 拍立得暖色调主题覆盖 */
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#C67B5C',
    primaryColorHover: '#D49472',
    primaryColorPressed: '#B56A4B',
    primaryColorSuppl: '#D4A574',
    infoColor: '#C67B5C',
    successColor: '#7BA87D',
    warningColor: '#D4A574',
    errorColor: '#D4745C',
    borderRadius: '8px',
    bodyColor: '#FBF7F0',
    cardColor: '#FFFDF9',
    modalColor: '#FFFDF9',
    popoverColor: '#FFFDF9',
    inputColor: '#FFFDF9',
    actionColor: '#F6F0E7',
    hoverColor: 'rgba(198, 123, 92, 0.06)',
    tableColorHover: 'rgba(198, 123, 92, 0.04)',
    dividerColor: 'rgba(180, 150, 120, 0.12)',
    borderColor: 'rgba(180, 150, 120, 0.15)',
    textColorBase: '#3D2E1F',
    textColor1: '#3D2E1F',
    textColor2: '#8B7355',
    textColor3: '#B5A590',
  },
  Card: {
    color: '#FFFDF9',
    borderColor: 'rgba(180, 150, 120, 0.12)',
    borderRadius: '12px',
  },
  Input: {
    color: '#FFFDF9',
    border: '1px solid rgba(180, 150, 120, 0.15)',
    borderHover: '1px solid #C67B5C',
    borderFocus: '1px solid #C67B5C',
    boxShadowFocus: '0 0 0 3px rgba(198, 123, 92, 0.1)',
  },
  Button: {
    colorPrimary: '#C67B5C',
    colorHoverPrimary: '#D49472',
    colorPressedPrimary: '#B56A4B',
    borderPrimary: '1px solid #C67B5C',
    borderHoverPrimary: '1px solid #D49472',
    borderPressedPrimary: '1px solid #B56A4B',
    textColorPrimary: '#FFFFFF',
  },
  Collapse: {
    titleTextColor: '#5C4630',
    dividerColor: 'rgba(180, 150, 120, 0.1)',
  },
  Progress: {
    fillColor: '#C67B5C',
  },
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background: #FBF7F0;
}
</style>
