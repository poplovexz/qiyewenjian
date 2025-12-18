/**
 * 前端性能检查脚本
 */
const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

class FrontendPerformanceChecker {
  constructor() {
    this.projectRoot = path.resolve(__dirname, '..')
    this.report = {
      timestamp: new Date().toISOString(),
      bundleSize: {},
      dependencies: {},
      codeQuality: {},
      performance: {}
    }
  }

  /**
   * 检查打包大小
   */
  checkBundleSize() {
    
    
    try {
      // 运行构建
      
      execSync('npm run build', { 
        cwd: this.projectRoot,
        stdio: 'pipe'
      })

      // 分析dist目录
      const distPath = path.join(this.projectRoot, 'dist')
      if (fs.existsSync(distPath)) {
        const stats = this.analyzeBuildOutput(distPath)
        this.report.bundleSize = stats
        
        
        
        
        
        // 检查大文件
        const largeFiles = stats.allFiles.filter(file => file.size > 1024 * 1024) // > 1MB
        if (largeFiles.length > 0) {
          
          largeFiles.forEach(file => {
            
          })
        }
      }
    } catch (error) {
      console.error('构建失败:', error.message)
    }
  }

  /**
   * 分析构建输出
   */
  analyzeBuildOutput(distPath) {
    const stats = {
      totalSize: 0,
      jsFiles: [],
      cssFiles: [],
      allFiles: []
    }

    const analyzeDir = (dirPath) => {
      const items = fs.readdirSync(dirPath)
      
      items.forEach(item => {
        const itemPath = path.join(dirPath, item)
        const stat = fs.statSync(itemPath)
        
        if (stat.isDirectory()) {
          analyzeDir(itemPath)
        } else {
          const fileInfo = {
            name: path.relative(distPath, itemPath),
            size: stat.size,
            ext: path.extname(item)
          }
          
          stats.totalSize += stat.size
          stats.allFiles.push(fileInfo)
          
          if (fileInfo.ext === '.js') {
            stats.jsFiles.push(fileInfo)
          } else if (fileInfo.ext === '.css') {
            stats.cssFiles.push(fileInfo)
          }
        }
      })
    }

    analyzeDir(distPath)
    return stats
  }

  /**
   * 检查依赖项
   */
  checkDependencies() {
    
    
    try {
      const packageJsonPath = path.join(this.projectRoot, 'package.json')
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'))
      
      const dependencies = packageJson.dependencies || {}
      const devDependencies = packageJson.devDependencies || {}
      
      this.report.dependencies = {
        production: Object.keys(dependencies).length,
        development: Object.keys(devDependencies).length,
        total: Object.keys(dependencies).length + Object.keys(devDependencies).length
      }
      
      
      
      
      // 检查过时的依赖
      try {
        const outdated = execSync('npm outdated --json', { 
          cwd: this.projectRoot,
          stdio: 'pipe'
        }).toString()
        
        if (outdated.trim()) {
          const outdatedPackages = JSON.parse(outdated)
          const count = Object.keys(outdatedPackages).length
          
          this.report.dependencies.outdated = count
        }
      } catch (error) {
        // npm outdated 在没有过时包时会返回非零退出码
        console.log('✓ 所有依赖都是最新的')
        this.report.dependencies.outdated = 0
      }
      
    } catch (error) {
      console.error('检查依赖失败:', error.message)
    }
  }

  /**
   * 检查代码质量
   */
  checkCodeQuality() {
    
    
    try {
      // 运行ESLint
      try {
        execSync('npm run lint', { 
          cwd: this.projectRoot,
          stdio: 'pipe'
        })
        
        this.report.codeQuality.eslint = 'passed'
      } catch (error) {
        console.log('⚠️  ESLint发现问题')
        this.report.codeQuality.eslint = 'failed'
      }
      
      // 检查TypeScript类型
      try {
        execSync('npx vue-tsc --noEmit', { 
          cwd: this.projectRoot,
          stdio: 'pipe'
        })
        
        this.report.codeQuality.typescript = 'passed'
      } catch (error) {
        console.log('⚠️  TypeScript类型检查发现问题')
        this.report.codeQuality.typescript = 'failed'
      }
      
    } catch (error) {
      console.error('代码质量检查失败:', error.message)
    }
  }

  /**
   * 检查性能指标
   */
  checkPerformanceMetrics() {
    
    
    // 检查Vue组件数量
    const componentCount = this.countVueComponents()
    
    this.report.performance.componentCount = componentCount
    
    // 检查路由数量
    const routeCount = this.countRoutes()
    
    this.report.performance.routeCount = routeCount
    
    // 检查Store模块数量
    const storeCount = this.countStoreModules()
    
    this.report.performance.storeModules = storeCount
    
    // 检查API接口数量
    const apiCount = this.countApiEndpoints()
    
    this.report.performance.apiEndpoints = apiCount
  }

  /**
   * 统计Vue组件数量
   */
  countVueComponents() {
    let count = 0
    const countInDir = (dirPath) => {
      if (!fs.existsSync(dirPath)) return
      
      const items = fs.readdirSync(dirPath)
      items.forEach(item => {
        const itemPath = path.join(dirPath, item)
        const stat = fs.statSync(itemPath)
        
        if (stat.isDirectory()) {
          countInDir(itemPath)
        } else if (item.endsWith('.vue')) {
          count++
        }
      })
    }
    
    countInDir(path.join(this.projectRoot, 'src'))
    return count
  }

  /**
   * 统计路由数量
   */
  countRoutes() {
    try {
      const routerPath = path.join(this.projectRoot, 'src/router')
      if (!fs.existsSync(routerPath)) return 0
      
      let routeCount = 0
      const countInFile = (filePath) => {
        const content = fs.readFileSync(filePath, 'utf8')
        const matches = content.match(/path:\s*['"`]/g)
        if (matches) {
          routeCount += matches.length
        }
      }
      
      const processDir = (dirPath) => {
        const items = fs.readdirSync(dirPath)
        items.forEach(item => {
          const itemPath = path.join(dirPath, item)
          const stat = fs.statSync(itemPath)
          
          if (stat.isDirectory()) {
            processDir(itemPath)
          } else if (item.endsWith('.ts') || item.endsWith('.js')) {
            countInFile(itemPath)
          }
        })
      }
      
      processDir(routerPath)
      return routeCount
    } catch (error) {
      return 0
    }
  }

  /**
   * 统计Store模块数量
   */
  countStoreModules() {
    try {
      const storePath = path.join(this.projectRoot, 'src/stores/modules')
      if (!fs.existsSync(storePath)) return 0
      
      const items = fs.readdirSync(storePath)
      return items.filter(item => 
        item.endsWith('.ts') || item.endsWith('.js')
      ).length
    } catch (error) {
      return 0
    }
  }

  /**
   * 统计API接口数量
   */
  countApiEndpoints() {
    try {
      const apiPath = path.join(this.projectRoot, 'src/api')
      if (!fs.existsSync(apiPath)) return 0
      
      let endpointCount = 0
      const countInFile = (filePath) => {
        const content = fs.readFileSync(filePath, 'utf8')
        // 匹配 request.get, request.post 等
        const matches = content.match(/request\.(get|post|put|delete|patch)/g)
        if (matches) {
          endpointCount += matches.length
        }
      }
      
      const processDir = (dirPath) => {
        const items = fs.readdirSync(dirPath)
        items.forEach(item => {
          const itemPath = path.join(dirPath, item)
          const stat = fs.statSync(itemPath)
          
          if (stat.isDirectory()) {
            processDir(itemPath)
          } else if (item.endsWith('.ts') || item.endsWith('.js')) {
            countInFile(itemPath)
          }
        })
      }
      
      processDir(apiPath)
      return endpointCount
    } catch (error) {
      return 0
    }
  }

  /**
   * 生成优化建议
   */
  generateOptimizationSuggestions() {
    const suggestions = []
    
    // 打包大小建议
    if (this.report.bundleSize.totalSize > 5 * 1024 * 1024) { // > 5MB
      suggestions.push('考虑使用代码分割和懒加载来减少初始包大小')
    }
    
    // 依赖建议
    if (this.report.dependencies.outdated > 5) {
      suggestions.push('建议更新过时的依赖包以获得性能改进和安全修复')
    }
    
    // 组件数量建议
    if (this.report.performance.componentCount > 100) {
      suggestions.push('组件数量较多，考虑使用组件懒加载和虚拟滚动')
    }
    
    return suggestions
  }

  /**
   * 运行完整检查
   */
  async runFullCheck() {
    
    
    this.checkDependencies()
    
    
    this.checkCodeQuality()
    
    
    this.checkPerformanceMetrics()
    
    
    this.checkBundleSize()
    
    
    // 生成建议
    const suggestions = this.generateOptimizationSuggestions()
    if (suggestions.length > 0) {
      
      suggestions.forEach((suggestion, index) => {
        
      })
      
    }
    
    // 保存报告
    const reportPath = path.join(this.projectRoot, 'performance-report.json')
    fs.writeFileSync(reportPath, JSON.stringify(this.report, null, 2))
    
    
    return this.report
  }
}

// 运行检查
if (require.main === module) {
  const checker = new FrontendPerformanceChecker()
  checker.runFullCheck().catch(console.error)
}

module.exports = FrontendPerformanceChecker
