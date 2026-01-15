<script setup lang="ts">
/**
 * 持仓管理组件
 * 支持添加、修改、删除持仓，自动保存到 localStorage
 */
import { ref, computed, onMounted, watch } from 'vue'

interface Position {
  ts_code: string
  name: string
  quantity: number
  cost_price: number
  current_price?: number
  profit?: number
  profit_pct?: number
  weight?: number
}

interface Portfolio {
  total_capital: number
  positions: Position[]
}

// 状态
const portfolio = ref<Portfolio>({
  total_capital: 100000,
  positions: []
})

const isEditing = ref(false)
const editingIndex = ref<number | null>(null)
const isLoading = ref(false)

// 表单
const formData = ref({
  ts_code: '',
  name: '',
  quantity: 100,
  cost_price: 0
})

// 计算属性
const totalMarketValue = computed(() => {
  return portfolio.value.positions.reduce((sum, pos) => {
    return sum + pos.quantity * pos.cost_price
  }, 0)
})

const totalProfit = computed(() => {
  return portfolio.value.positions.reduce((sum, pos) => {
    return sum + (pos.profit || 0)
  }, 0)
})

// 初始化：从 localStorage 加载
onMounted(() => {
  const saved = localStorage.getItem('portfolio')
  if (saved) {
    try {
      portfolio.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载持仓数据失败', e)
    }
  }
  // 刷新行情
  refreshQuotes()
})

// 监听变化，自动保存
watch(portfolio, (newVal) => {
  localStorage.setItem('portfolio', JSON.stringify(newVal))
}, { deep: true })

// 刷新实时行情
async function refreshQuotes() {
  if (portfolio.value.positions.length === 0) return
  
  isLoading.value = true
  try {
    // 调用后端获取实时行情
    for (const pos of portfolio.value.positions) {
      try {
        const response = await fetch(`/api/stock/quote?ts_code=${pos.ts_code}`)
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.data) {
            pos.current_price = data.data.price
            pos.name = data.data.name || pos.name
            const currentPrice = pos.current_price || pos.cost_price
            pos.profit = (currentPrice - pos.cost_price) * pos.quantity
            pos.profit_pct = pos.cost_price > 0 
              ? ((currentPrice / pos.cost_price) - 1) * 100 
              : 0
          }
        }
      } catch (e) {
        console.error(`获取 ${pos.ts_code} 行情失败`)
      }
    }
    // 重新计算仓位占比
    updateWeights()
  } finally {
    isLoading.value = false
  }
}

// 更新仓位占比
function updateWeights() {
  const total = portfolio.value.total_capital
  for (const pos of portfolio.value.positions) {
    const value = pos.quantity * pos.cost_price
    pos.weight = total > 0 ? (value / total) * 100 : 0
  }
}

// 添加/编辑持仓
function savePosition() {
  // 验证
  if (!formData.value.ts_code) {
    alert('请输入股票代码')
    return
  }
  if (formData.value.quantity <= 0 || formData.value.quantity % 100 !== 0) {
    alert('持仓数量必须是100的正整数倍')
    return
  }
  if (formData.value.cost_price <= 0) {
    alert('请输入有效的成本价')
    return
  }
  
  const position: Position = {
    ts_code: formData.value.ts_code.toUpperCase(),
    name: formData.value.name || formData.value.ts_code,
    quantity: formData.value.quantity,
    cost_price: formData.value.cost_price
  }
  
  if (editingIndex.value !== null) {
    // 编辑模式
    portfolio.value.positions[editingIndex.value] = position
  } else {
    // 新增模式
    portfolio.value.positions.push(position)
  }
  
  // 重置表单
  resetForm()
  updateWeights()
}

// 编辑持仓
function editPosition(index: number) {
  const pos = portfolio.value.positions[index]
  if (!pos) return
  formData.value = {
    ts_code: pos.ts_code,
    name: pos.name,
    quantity: pos.quantity,
    cost_price: pos.cost_price
  }
  editingIndex.value = index
  isEditing.value = true
}

// 删除持仓
function deletePosition(index: number) {
  if (confirm('确定要删除这条持仓记录吗？')) {
    portfolio.value.positions.splice(index, 1)
    updateWeights()
  }
}

// 重置表单
function resetForm() {
  formData.value = {
    ts_code: '',
    name: '',
    quantity: 100,
    cost_price: 0
  }
  editingIndex.value = null
  isEditing.value = false
}

// 格式化数字
function formatNumber(num: number, decimals = 2): string {
  return num.toLocaleString('zh-CN', { 
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals 
  })
}

// 格式化百分比
function formatPercent(num: number): string {
  const sign = num >= 0 ? '+' : ''
  return sign + num.toFixed(2) + '%'
}
</script>

<template>
  <div class="portfolio-manager">
    <div class="section-header">
      <h2>📊 我的持仓</h2>
      <div class="header-actions">
        <button class="btn btn-secondary btn-sm" @click="refreshQuotes" :disabled="isLoading">
          {{ isLoading ? '刷新中...' : '🔄 刷新行情' }}
        </button>
      </div>
    </div>

    <!-- 总资金设置 -->
    <div class="capital-section">
      <label>总投入资金：</label>
      <div class="capital-input">
        <span class="currency">¥</span>
        <input 
          type="number" 
          v-model.number="portfolio.total_capital" 
          min="0"
          step="10000"
        />
      </div>
      <div class="capital-stats">
        <span>持仓市值: ¥{{ formatNumber(totalMarketValue) }}</span>
        <span :class="totalProfit >= 0 ? 'profit' : 'loss'">
          盈亏: {{ totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalProfit) }}
        </span>
      </div>
    </div>

    <!-- 添加/编辑表单 -->
    <div class="add-form">
      <div class="form-row">
        <div class="form-group">
          <label>股票代码</label>
          <input 
            type="text" 
            v-model="formData.ts_code" 
            placeholder="如 000001.SZ"
            @blur="formData.ts_code = formData.ts_code.toUpperCase()"
          />
        </div>
        <div class="form-group">
          <label>股票名称</label>
          <input type="text" v-model="formData.name" placeholder="可选" />
        </div>
        <div class="form-group">
          <label>持有数量</label>
          <input 
            type="number" 
            v-model.number="formData.quantity" 
            min="100" 
            step="100"
            placeholder="100的整数倍"
          />
        </div>
        <div class="form-group">
          <label>成本价</label>
          <input 
            type="number" 
            v-model.number="formData.cost_price" 
            min="0" 
            step="0.01"
            placeholder="买入均价"
          />
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" @click="savePosition">
            {{ editingIndex !== null ? '保存修改' : '➕ 添加' }}
          </button>
          <button v-if="editingIndex !== null" class="btn btn-secondary" @click="resetForm">
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 持仓列表 -->
    <div class="positions-list">
      <div v-if="portfolio.positions.length === 0" class="empty-state">
        <p>暂无持仓记录，请添加您的持仓</p>
      </div>
      
      <table v-else class="positions-table">
        <thead>
          <tr>
            <th>股票</th>
            <th>数量</th>
            <th>成本价</th>
            <th>现价</th>
            <th>盈亏</th>
            <th>仓位</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(pos, index) in portfolio.positions" :key="pos.ts_code">
            <td class="stock-cell">
              <span class="stock-name">{{ pos.name || pos.ts_code }}</span>
              <span class="stock-code">{{ pos.ts_code }}</span>
            </td>
            <td>{{ pos.quantity }}</td>
            <td>¥{{ formatNumber(pos.cost_price) }}</td>
            <td>
              <span v-if="pos.current_price">¥{{ formatNumber(pos.current_price) }}</span>
              <span v-else class="no-data">--</span>
            </td>
            <td>
              <div v-if="pos.profit !== undefined" :class="pos.profit >= 0 ? 'profit' : 'loss'">
                <span>{{ pos.profit >= 0 ? '+' : '' }}¥{{ formatNumber(pos.profit) }}</span>
                <span class="profit-pct">{{ formatPercent(pos.profit_pct || 0) }}</span>
              </div>
              <span v-else class="no-data">--</span>
            </td>
            <td>{{ pos.weight ? pos.weight.toFixed(1) + '%' : '--' }}</td>
            <td class="actions-cell">
              <button class="action-btn edit" @click="editPosition(index)">✏️</button>
              <button class="action-btn delete" @click="deletePosition(index)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.portfolio-manager {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--text-primary, #fff);
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 总资金 */
.capital-section {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--bg-secondary, #1e1e2e);
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.capital-section label {
  color: var(--text-secondary, #888);
  font-size: 0.9rem;
}

.capital-input {
  display: flex;
  align-items: center;
  background: var(--bg-tertiary, #2a2a3e);
  border-radius: 8px;
  padding: 0 12px;
}

.currency {
  color: var(--text-secondary, #888);
  font-size: 1.1rem;
}

.capital-input input {
  background: none;
  border: none;
  color: var(--text-primary, #fff);
  font-size: 1.2rem;
  font-weight: 600;
  padding: 10px;
  width: 140px;
}

.capital-input input:focus {
  outline: none;
}

.capital-stats {
  display: flex;
  gap: 24px;
  margin-left: auto;
  font-size: 0.9rem;
}

.capital-stats span {
  color: var(--text-secondary, #888);
}

/* 添加表单 */
.add-form {
  background: var(--bg-secondary, #1e1e2e);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 140px;
}

.form-group label {
  font-size: 0.8rem;
  color: var(--text-secondary, #888);
}

.form-group input {
  background: var(--bg-tertiary, #2a2a3e);
  border: 1px solid var(--border-color, #333);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--text-primary, #fff);
  font-size: 0.95rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color, #8b5cf6);
}

.form-actions {
  display: flex;
  gap: 10px;
}

/* 持仓列表 */
.positions-list {
  background: var(--bg-secondary, #1e1e2e);
  border-radius: 12px;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary, #888);
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
}

.positions-table th,
.positions-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #333);
}

.positions-table th {
  background: var(--bg-tertiary, #2a2a3e);
  color: var(--text-secondary, #888);
  font-weight: 500;
  font-size: 0.85rem;
}

.positions-table tbody tr:hover {
  background: rgba(139, 92, 246, 0.05);
}

.stock-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-name {
  font-weight: 500;
  color: var(--text-primary, #fff);
}

.stock-code {
  font-size: 0.8rem;
  color: var(--text-secondary, #888);
}

.profit {
  color: #22c55e;
}

.loss {
  color: #ef4444;
}

.profit-pct {
  display: block;
  font-size: 0.8rem;
  opacity: 0.8;
}

.no-data {
  color: var(--text-muted, #555);
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: var(--bg-tertiary, #2a2a3e);
}

/* 按钮 */
.btn {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 0.85rem;
}

.btn-primary {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.btn-secondary {
  background: var(--bg-tertiary, #2a2a3e);
  color: var(--text-primary, #fff);
  border: 1px solid var(--border-color, #333);
}

.btn-secondary:hover {
  background: var(--bg-hover, #333);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
