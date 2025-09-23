import { useState, useEffect } from 'react';

interface AgentCommunicationProps {
  isActive: boolean;
}

interface Agent {
  id: string;
  name: string;
  icon: string;
  role: string;
  status: 'idle' | 'thinking' | 'communicating' | 'responding';
}

const agents: Agent[] = [
  {
    id: '1',
    name: 'Captain Agent',
    icon: '/icons/7d1d4270-64e2-4469-8b7c-cffbc85b972c.jpeg',
    role: 'Control & Coordinate',
    status: 'idle'
  },
  {
    id: '2', 
    name: 'Scout Agent',
    icon: '/icons/6ed5f0f6-1984-48bd-9d1a-33dd22dd3e9e.jpeg',
    role: 'Extract frame  & Masking',
    status: 'idle'
  },
  {
    id: '3',
    name: 'Graph Builder Agent',
    icon: '/icons/f4552888-0e17-4b53-a25e-53e9176c285a.jpeg',
    role: 'Build graph & Analyze',
    status: 'idle'
  },
  {
    id: '4',
    name: 'Inspector Agent',
    icon: '/icons/d1bb9a8b-33ff-446f-9bbf-c4ee80de914d.jpeg',
    role: 'Recheck & Request',
    status: 'idle'
  },
  {
    id: '5',
    name: 'Messenger Agent',
    icon: '/icons/1ea04601-d485-402a-bc34-a96100f40737.jpeg',
    role: 'Answer user',
    status: 'idle'
  }
];

export function AgentCommunication({ isActive }: AgentCommunicationProps) {
  const [currentAgents, setCurrentAgents] = useState<Agent[]>(agents);

  useEffect(() => {
    if (!isActive) {
      setCurrentAgents(agents.map(agent => ({ ...agent, status: 'idle' })));
      return;
    }

    const simulateCommunication = () => {
      const steps = [
        // Step 1: Manager starts thinking
        () => setCurrentAgents(prev => prev.map(agent => 
          agent.id === '1' ? { ...agent, status: 'thinking' } : agent
        )),
        
        // Step 2: Manager communicates with Research Agent
        () => setCurrentAgents(prev => prev.map(agent => 
          agent.id === '1' ? { ...agent, status: 'communicating' } :
          agent.id === '2' ? { ...agent, status: 'thinking' } : agent
        )),
        
        // Step 3: Research Agent and Video Processor work
        () => setCurrentAgents(prev => prev.map(agent => 
          agent.id === '2' ? { ...agent, status: 'communicating' } :
          agent.id === '3' ? { ...agent, status: 'thinking' } : agent
        )),
        
        // Step 4: Knowledge Base joins
        () => setCurrentAgents(prev => prev.map(agent => 
          agent.id === '3' ? { ...agent, status: 'communicating' } :
          agent.id === '4' ? { ...agent, status: 'thinking' } : agent
        )),
        
        // Step 5: All collaborate for final response
        () => setCurrentAgents(prev => prev.map(agent => 
          agent.id === '5' ? { ...agent, status: 'responding' } :
          ['2', '3', '4'].includes(agent.id) ? { ...agent, status: 'communicating' } :
          agent.id === '1' ? { ...agent, status: 'thinking' } : agent
        )),
      ];

      let currentStep = 0;
      const interval = setInterval(() => {
        currentStep = (currentStep + 1) % steps.length;
        steps[currentStep]();
      }, 1500);

      return () => clearInterval(interval);
    };

    const cleanup = simulateCommunication();
    return cleanup;
  }, [isActive]);

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'thinking': return 'bg-blue-500 animate-pulse';
      case 'communicating': return 'bg-green-500';
      case 'responding': return 'bg-purple-500 animate-pulse';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = (status: Agent['status']) => {
    switch (status) {
      case 'thinking': return 'Đang suy nghĩ...';
      case 'communicating': return 'Đang giao tiếp...';
      case 'responding': return 'Đang phản hồi...';
      default: return 'Sẵn sàng';
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-sm font-semibold text-amber-800 mb-2">
          {isActive ? '🤖 Hệ thống AI đang xử lý' : '🤖 Hệ thống AI sẵn sàng'}
        </h3>
        {isActive && (
          <div className="text-xs text-amber-600">
            Các agent đang phối hợp để tạo câu trả lời tốt nhất...
          </div>
        )}
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-2 gap-3">
        {currentAgents.map((agent) => (
          <div
            key={agent.id}
            className={`relative p-3 rounded-xl border-2 transition-all duration-500 ${
              agent.status !== 'idle' 
                ? 'border-amber-300 bg-gradient-to-br from-yellow-50 to-amber-100 shadow-md scale-105' 
                : 'border-gray-200 bg-white shadow-sm hover:shadow-md'
            }`}
          >
            {/* Agent Icon */}
            <div className="flex items-center justify-center mb-2">
              <div className={`relative w-10 h-10 rounded-full overflow-hidden border-2 ${
                agent.status !== 'idle' ? 'border-amber-400' : 'border-gray-300'
              }`}>
                <img 
                  src={agent.icon} 
                  alt={agent.name}
                  className="w-full h-full object-cover"
                />
                
                {/* Status indicator */}
                <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(agent.status)}`} />
              </div>
            </div>

            {/* Agent Info */}
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-800 truncate mb-1">
                {agent.name}
              </div>
              <div className="text-[10px] text-gray-500 truncate mb-2">
                {agent.role}
              </div>
              
              {/* Status */}
              <div className={`text-[10px] px-2 py-1 rounded-full ${
                agent.status !== 'idle' 
                  ? 'bg-amber-200 text-amber-800' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {getStatusText(agent.status)}
              </div>
            </div>

            {/* Communication Lines - when active */}
            {agent.status === 'communicating' && (
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 w-12 h-12 border border-green-400 rounded-full animate-ping opacity-60 transform -translate-x-1/2 -translate-y-1/2" />
                <div className="absolute top-1/2 left-1/2 w-8 h-8 border border-green-500 rounded-full animate-pulse opacity-80 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Global Activity Indicator */}
      {isActive && (
        <div className="mt-4 p-3 bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg">
          <div className="flex items-center justify-center space-x-2">
            <div className="flex space-x-1">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-amber-500 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 0.1}s` }}
                />
              ))}
            </div>
            <span className="text-xs text-amber-700 ml-2">
              Đang xử lý yêu cầu...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}