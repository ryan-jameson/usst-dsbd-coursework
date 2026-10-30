export const trainingModes = [
  {
    value: 'mirror',
    name: '镜像同步',
    desc: '双手对称运动，如同照镜子 (基础)',
    icon: '🦋',
    difficulty: 1
  },
  {
    value: 'parallel',
    name: '平行同向',
    desc: '双手向同一方向移动，克服对称本能 (进阶)',
    icon: '🛤️',
    difficulty: 2
  },
  {
    value: 'dissociation',
    name: '双侧分离',
    desc: '左圆右方，左右脑独立处理不同任务 (挑战)',
    icon: '🔀',
    difficulty: 3
  }
]

export const taskTypes = [
  { label: '轨迹描摹', value: 'trace' },
  { label: '自由创作', value: 'free' }
]
