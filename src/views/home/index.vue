<script setup>
import { ref } from 'vue'
import { House, Setting, Document, Expand, Fold, ArrowDown, User } from '@element-plus/icons-vue'

const isCollapse = ref(false)

const handleCollapse = () => {
    isCollapse.value = !isCollapse.value
}
</script>

<template>
    <div class="home-container">
        <!-- 侧边栏 -->
        <el-aside :width="isCollapse ? '64px' : '200px'" class="aside">
            <div class="sidebar-logo-container" :class="{ 'collapse': isCollapse }">
                <img src="/logo.png" class="sidebar-logo" alt="logo" />
                <h1 class="sidebar-title" v-if="!isCollapse">爱特工作室</h1>
            </div>
            <el-menu :collapse="isCollapse" :collapse-transition="false" class="el-menu-vertical"
                background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF" router style="height: calc(100% - 200px)">
                <el-menu-item index="/">
                    <el-icon>
                        <House />
                    </el-icon>
                    <template #title>首页</template>
                </el-menu-item>
                <el-menu-item index="/global-config">
                    <el-icon>
                        <Setting />
                    </el-icon>
                    <template #title>全局配置</template>
                </el-menu-item>
                <el-menu-item index="/domain-add">
                    <el-icon>
                        <Document />
                    </el-icon>
                    <template #title>域名添加</template>
                </el-menu-item>
            </el-menu>
        </el-aside>

        <el-container class="main-container">
            <!-- 顶部导航栏 -->
            <el-header class="header">
                <div class="header-left">
                    <el-button type="text" @click="handleCollapse">
                        <el-icon>
                            <component :is="isCollapse ? 'Expand' : 'Fold'" />
                        </el-icon>
                    </el-button>
                </div>
                <div class="header-right">
                    <el-dropdown>
                        <span class="el-dropdown-link">
                            <el-icon class="mr-1">
                                <User />
                            </el-icon>
                            管理员
                            <el-icon class="el-icon--right">
                                <ArrowDown />
                            </el-icon>
                        </span>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item>个人信息</el-dropdown-item>
                                <el-dropdown-item>退出登录</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </el-header>

            <!-- 主要内容区域 -->
            <el-main class="main">
                <router-view />
            </el-main>
        </el-container>
    </div>
</template>

<style scoped>
.home-container {
    height: 100vh;
    display: flex;
}

.aside {
    transition: width 0.3s;
    background-color: #304156;
}

.el-menu-vertical {
    height: 100%;
    border-right: none;
}

.main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.header {
    background-color: #fff;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-left {
    display: flex;
    align-items: center;
}

.sidebar-logo-container {
    height: 50px;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #2b2f3a;
    transition: all 0.3s;
}

.sidebar-logo-container.collapse {
    padding: 10px;
}

.sidebar-logo {
    width: 32px;
    height: 32px;
    object-fit: contain;
}

.sidebar-title {
    margin-left: 12px;
    color: #fff;
    font-weight: 600;
    font-size: 14px;
    white-space: nowrap;
}

.header-right {
    display: flex;
    align-items: center;
}

.el-dropdown-link {
    cursor: pointer;
    display: flex;
    align-items: center;
    color: #409EFF;
}

.main {
    background-color: #f0f2f5;
    height: calc(100vh - 60px);
    overflow-y: auto;
}

.main::-webkit-scrollbar {
    width: 6px;
}

.main::-webkit-scrollbar-thumb {
    background-color: #909399;
    border-radius: 3px;
}

.main::-webkit-scrollbar-track {
    background-color: #f0f2f5;
}
</style>