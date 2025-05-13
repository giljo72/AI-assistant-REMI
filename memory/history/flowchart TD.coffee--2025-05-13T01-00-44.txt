flowchart TD
    %% Main components with bold colors
    App[App.tsx]:::main
    MainLayout[MainLayout.tsx]:::component
    ProjectView[ProjectManagerView.tsx]:::component
    ChatView[ChatView.tsx]:::component
    DocView[DocumentView.tsx]:::component
    ProjFiles[ProjectFileManager.tsx]:::component
    MainFiles[MainFileManager.tsx]:::component
    SearchRes[SearchFilesResults.tsx]:::component
    TagAddModal[TagAndAddFileModal.tsx]:::component

    %% App container and first level navigation
    App --> MainLayout
    App --> ProjectView
    App --> ChatView
    App --> DocView
    App --> ProjFiles
    App --> MainFiles
    App --> SearchRes
    App --> TagAddModal

    %% Navigation flows between components
    ProjectView -->|"onOpenChat()"|ChatView:::highlight
    ProjectView -->|"onOpenFiles()"|ProjFiles:::highlight
    
    ProjFiles -->|"onReturn()"|ProjectView:::highlight
    ProjFiles -->|"Browse Global Files"|MainFiles:::highlight
    
    MainFiles -->|"onReturn()"|ProjFiles:::highlight
    MainFiles -->|"Search Files"|SearchRes:::highlight
    MainFiles -->|"browse()"|TagAddModal:::highlight
    
    SearchRes -->|"onAttachFiles()"|ProjFiles:::highlight
    SearchRes -->|"onClose()"|ProjFiles:::highlight
    
    TagAddModal -->|"onProcessFiles()"|MainFiles:::highlight

    %% File directory structure
    Directory[File Directory Structure]:::title
    
    src[src/]:::folder
    components[components/]:::folder
    file[file/]:::folder
    modals[modals/]:::folder
    project[project/]:::folder
    chat[chat/]:::folder
    document[document/]:::folder
    layout[layout/]:::folder
    
    Directory --> src
    src --> components
    src --> App
    
    components --> file
    components --> modals
    components --> project
    components --> chat
    components --> document
    components --> layout
    
    file --> ProjFiles
    file --> MainFiles
    file --> SearchRes
    modals --> TagAddModal
    project --> ProjectView
    chat --> ChatView
    document --> DocView
    layout --> MainLayout

    %% Styling for different node types
    classDef main fill:#1E40AF,color:white,stroke:#1E3A8A,stroke-width:3px
    classDef component fill:#3B82F6,color:white,stroke:#2563EB,stroke-width:2px
    classDef folder fill:#374151,color:#D1D5DB,stroke:#4B5563,stroke-width:1px
    classDef highlight color:#F59E0B,stroke:#F59E0B,stroke-width:2px
    classDef title fill:none,color:#F59E0B,stroke:none,font-size:16px,font-weight:bold
    
    %% Make all navigation flow lines thicker and colored
    linkStyle default stroke:#6366F1,stroke-width:2px