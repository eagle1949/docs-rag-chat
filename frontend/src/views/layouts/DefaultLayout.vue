<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="layout">
    <nav class="navbar">
      <div class="nav-brand">LLMOps</div>
      <div class="nav-links">
        <RouterLink to="/home" class="nav-link">首页</RouterLink>
        <RouterLink to="/space/apps" class="nav-link">AI应用</RouterLink>
        <RouterLink to="/rag" class="nav-link">文档问答</RouterLink>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.navbar {
  background-color: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  font-size: 20px;
  font-weight: bold;
  color: #165dff;
}

.nav-links {
  display: flex;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-size: 14px;
  transition: color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #165dff;
}

.main-content {
  padding: 20px;
}
</style>
