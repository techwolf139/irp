/// <reference types="vite/client" />

declare module 'reactflow' {
  export interface NodeTypes {
    entry: boolean
    exit: boolean
    agent: boolean
    graph: boolean
    loop: boolean
  }
}

export {}
