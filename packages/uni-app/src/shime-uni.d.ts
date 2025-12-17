export {}

declare module "vue" {
  type Hooks = App.AppInstance & Page.PageInstance;
  interface ComponentCustomOptions extends Hooks {}
}

// uv-ui 组件库类型声明
declare module '@climblee/uv-ui' {
  const content: any
  export default content
}