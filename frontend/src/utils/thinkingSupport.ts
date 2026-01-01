export type ThinkingMode = 'none' | 'level' | 'budget'

export interface ThinkingLevelOption {
  value: 'minimal' | 'low' | 'medium' | 'high'
  label: string
}

export interface BudgetRangeInfo {
  min: number
  max: number
  step?: number
  allowZero?: boolean
  allowDynamic?: boolean  // 是否允许 -1 动态思考
  default?: number
  description?: string
}

export interface ThinkingSupportInfo {
  supported: boolean
  mode: ThinkingMode
  includeThoughts: boolean
  levelOptions?: ThinkingLevelOption[]
  budgetRange?: BudgetRangeInfo
  note?: string
}

interface ThinkingSupportOptions {
  supportsImage?: boolean
}

const NONE_PATTERNS = [
  'gemini-2.5-flash-image',
  'gemini-2.5-flash-preview-tts',
  'gemini-2.5-pro-preview-tts',
  'gemini-2.0-flash-preview-image-generation',
  'gemini-2.0-flash-lite'
]

const defaultInfo: ThinkingSupportInfo = {
  supported: false,
  mode: 'none',
  includeThoughts: false,
  note: '当前模型不支持思考配置'
}

export const getThinkingSupport = (
  modelId?: string,
  options: ThinkingSupportOptions = {}
): ThinkingSupportInfo => {
  if (!modelId) return defaultInfo
  const id = modelId.toLowerCase()

  if (NONE_PATTERNS.some(pattern => id.includes(pattern))) {
    return {
      supported: false,
      mode: 'none',
      includeThoughts: false,
      note: '该模型禁用了思考配置'
    }
  }

  if (options.supportsImage) {
    return {
      supported: true,
      mode: 'none',
      includeThoughts: true,
      note: '图像生成模型仅支持 includeThoughts，不支持 thinkingLevel/thinkingBudget'
    }
  }

  if (id.startsWith('gemini-3-pro')) {
    return {
      supported: true,
      mode: 'level',
      includeThoughts: true,
      levelOptions: [
        { value: 'low', label: 'low - 低延迟思考' },
        { value: 'high', label: 'high - 深度推理 (默认)' }
      ],
      note: 'Gemini 3 Pro 支持思考等级 (low/high)'
    }
  }

  if (id.startsWith('gemini-3-flash')) {
    return {
      supported: true,
      mode: 'level',
      includeThoughts: true,
      levelOptions: [
        { value: 'minimal', label: 'minimal - 几乎不思考' },
        { value: 'low', label: 'low - 简要思考' },
        { value: 'medium', label: 'medium - 平衡速度与质量' },
        { value: 'high', label: 'high - 深度推理' }
      ],
      note: 'Gemini 3 Flash 支持 minimal/low/medium/high'
    }
  }

  if (id.startsWith('gemini-2.5-flash-lite')) {
    return {
      supported: true,
      mode: 'budget',
      includeThoughts: true,
      budgetRange: {
        min: 512,
        max: 24576,
        allowZero: true,
        allowDynamic: true,
        default: 0,
        description: '512-24576，0 禁用，-1 动态思考'
      },
      note: 'Gemini 2.5 Flash-Lite 使用 thinkingBudget (512-24576)'
    }
  }

  if (id.startsWith('gemini-2.5-flash')) {
    return {
      supported: true,
      mode: 'budget',
      includeThoughts: true,
      budgetRange: {
        min: 0,
        max: 24576,
        allowZero: true,
        allowDynamic: true,
        default: -1,
        description: '0-24576，0 禁用，-1 动态思考'
      },
      note: 'Gemini 2.5 Flash 使用 thinkingBudget (0-24576)'
    }
  }

  if (id.startsWith('gemini-2.5-pro')) {
    return {
      supported: true,
      mode: 'budget',
      includeThoughts: true,
      budgetRange: {
        min: 128,
        max: 32768,
        allowZero: false,
        allowDynamic: true,
        default: -1,
        description: '128-32768，-1 代表动态思考，不可设置为 0'
      },
      note: 'Gemini 2.5 Pro 使用 thinkingBudget (128-32768)'
    }
  }

  if (id.startsWith('gemini-2.0-flash')) {
    return {
      supported: true,
      mode: 'budget',
      includeThoughts: true,
      budgetRange: {
        min: 0,
        max: 16384,
        allowZero: true,
        allowDynamic: true,
        default: -1,
        description: '实验性支持，建议 0-16384 或 -1 动态'
      },
      note: 'Gemini 2.0 Flash 提供实验性 thinkingBudget'
    }
  }

  // 其它未知模型默认不支持
  return defaultInfo
}
