import { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react';

interface ThoughtBoxProps {
  author: string;
  content: string;
  type?: 'thought' | 'function';
  data?: unknown;
  compact?: boolean;
}

export function ThoughtBox({ author, content, type = 'thought', data, compact = false }: ThoughtBoxProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getIcon = () => {
    return type === 'thought' ? '💭' : '🔧';
  };

  const getTitle = () => {
    return type === 'thought' ? `Suy nghĩ (${author})` : content;
  };

  const getDisplayContent = () => {
    // For function types, if content is already detailed (not just generic text), use it directly
    if (type === 'function' && content && !content.startsWith('🔧') && !content.startsWith('📊')) {
      return content;
    }
    
    // Fallback to data parsing for legacy or detailed display
    if (type === 'function' && data) {
      // Handle function call
      const funcCallData = data as { functionCall?: { name: string; args?: Record<string, unknown> } };
      if (funcCallData.functionCall) {
        const args = funcCallData.functionCall.args;
        if (args) {
          let argsText = '';
          Object.entries(args).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              argsText += `${key}: ${value.join(', ')}\n`;
            } else {
              argsText += `${key}: ${JSON.stringify(value, null, 2)}\n`;
            }
          });
          return argsText.trim();
        }
        return `Gọi function: ${funcCallData.functionCall.name}`;
      }

      // Handle function response
      const funcResponseData = data as { name?: string; response?: { result?: Array<{ query?: string; results?: { faq?: string; document?: string } }> } };
      if (funcResponseData.response?.result && Array.isArray(funcResponseData.response.result)) {
        let result = '';
        funcResponseData.response.result.forEach((item, index: number) => {
          if (item.query) {
            result += `🔍 Truy vấn: ${item.query}\n\n`;
          }
          if (item.results) {
            if (item.results.faq && item.results.faq !== "Không tìm thấy tài liệu nào liên quan đến yêu cầu của bạn.") {
              result += `📋 FAQ:\n${item.results.faq}\n\n`;
            }
            if (item.results.document && item.results.document !== "Không tìm thấy tài liệu nào liên quan đến yêu cầu của bạn.") {
              result += `📄 Tài liệu:\n${item.results.document}\n\n`;
            }
            if (item.results.faq === "Không tìm thấy tài liệu nào liên quan đến yêu cầu của bạn." && 
                item.results.document === "Không tìm thấy tài liệu nào liên quan đến yêu cầu của bạn.") {
              result += `⚠️ Không tìm thấy tài liệu liên quan\n\n`;
            }
          }            
          if (funcResponseData.response?.result && index < funcResponseData.response.result.length - 1) {
            result += '---\n\n';
          }
        });
        return result.trim() || 'Không có kết quả';
      }

      // Fallback
      return JSON.stringify(data, null, 2);
    }
    return content;
  };

  // Không render component nếu không có content để hiển thị hoặc chỉ là function call đơn giản
  const displayContent = getDisplayContent();
  if (!displayContent.trim()) {
    return null;
  }
  
  // Ẩn function calls đơn giản (chỉ hiển thị arguments)
  if (type === 'function' && data) {
    const funcCallData = data as { functionCall?: { name: string; args?: Record<string, unknown> } };
    if (funcCallData.functionCall && !funcCallData.functionCall.args) {
      return null; // Ẩn function call không có args
    }
    // Ẩn function call chỉ có query đơn giản
    if (funcCallData.functionCall?.args) {
      const args = funcCallData.functionCall.args;
      const hasOnlySimpleQuery = Object.keys(args).length === 1 && 
                                 Object.keys(args)[0] === 'queries' &&
                                 Array.isArray(args.queries) &&
                                 args.queries.length === 1;
      if (hasOnlySimpleQuery) {
        return null; // Ẩn function call chỉ có 1 query đơn giản
      }
    }
  }

  if (compact) {
    return (
      <div className="border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800/50">
        {/* Compact Header */}
        <div 
          className="flex items-center justify-between p-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors rounded-md"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className="text-sm">{getIcon()}</span>
            <span className="font-medium text-xs text-gray-700 dark:text-gray-300 truncate">
              {type === 'thought' ? `Suy nghĩ` : getTitle()}
            </span>
          </div>
          <div className="text-gray-500 dark:text-gray-400 flex-shrink-0">
            {isExpanded ? (
              <ChevronUpIcon size={12} />
            ) : (
              <ChevronDownIcon size={12} />
            )}
          </div>
        </div>

        {/* Compact Expandable Content */}
        {isExpanded && (
          <div className="px-2 pb-2 border-t border-gray-200 dark:border-gray-700">
            <div className="pt-2 text-xs text-gray-600 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
              {displayContent}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="my-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800/50">
      {/* Header - Always visible */}
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors rounded-t-lg"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{getIcon()}</span>
          <span className="font-medium text-sm text-gray-700 dark:text-gray-300">
            {getTitle()}
          </span>
        </div>
        <div className="text-gray-500 dark:text-gray-400">
          {isExpanded ? (
            <ChevronUpIcon size={16} />
          ) : (
            <ChevronDownIcon size={16} />
          )}
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-gray-200 dark:border-gray-700">
          <div className="pt-3 text-sm text-gray-600 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {displayContent}
          </div>
        </div>
      )}
    </div>
  );
}
