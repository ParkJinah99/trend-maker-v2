import { PanelGroup, Panel } from 'react-resizable-panels';
import { Chat } from '../pages/chat/chat';
import '../App.css'; // for tailwind + panel styles

export default function MainLayout() {
  return (
    <PanelGroup direction="horizontal" className="h-screen w-full">
      <Panel defaultSize={50} minSize={20} maxSize={80}>
        <div className="h-full bg-gray-100 dark:bg-gray-800 p-4 overflow-auto">
          <h2 className="text-xl font-bold mb-4">Dashboard</h2>
        </div>
      </Panel>
      <Panel>
        <div className="h-full bg-white dark:bg-gray-900 p-4 overflow-auto">
          <Chat />
        </div>
      </Panel>
    </PanelGroup>
  );
}
