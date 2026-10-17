import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Sparkles, 
  Send, 
  Terminal, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  ArrowRight, 
  Cpu, 
  Gauge, 
  Info,
  Clock,
  ShieldCheck,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { fetchAgentStatus, planWithAgent } from '../services/api';
import { formatINR } from '../utils/formatters';

const PRESET_PROMPTS = [
  "Optimize my trip to fit a budget of ₹15,000",
  "Shorten the trip to 2 days and cut unnecessary costs",
  "Upgrade to comfort travel style and focus on heritage",
  "Check whether my budget and duration are feasible"
];

export default function AgentPlannerPanel({
  currentPlan,
  formData,
  onPlanUpdated,
  isAdapting,
  setIsAdapting
}) {
  const [userRequest, setUserRequest] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState(null);
  const [agentResponse, setAgentResponse] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [showTraces, setShowTraces] = useState(true);

  // Check Strands Decider provider status on mount
  useEffect(() => {
    let isMounted = true;
    async function loadStatus() {
      try {
        const res = await fetchAgentStatus();
        if (isMounted) setAgentStatus(res);
      } catch (err) {
        if (isMounted) {
          setAgentStatus({
            status: 'error',
            model: 'StrandsAgents/strands-decider-2B',
            provider: { available: false, error: err.message }
          });
        }
      }
    }
    loadStatus();
    return () => { isMounted = false; };
  }, []);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!userRequest.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMessage(null);
    if (setIsAdapting) setIsAdapting(true);

    try {
      const response = await planWithAgent({
        userRequest: userRequest.trim(),
        destinationId: currentPlan?.destination?.id || formData?.destinationId,
        destinationName: currentPlan?.destination?.name || formData?.customDestinationName,
        startingCity: currentPlan?.startingCity || formData?.startingCity,
        duration: currentPlan?.numDays || formData?.days,
        budget: currentPlan?.userBudget || formData?.budget,
        travelStyle: currentPlan?.travelStyle || formData?.travelStyle,
        interests: currentPlan?.destination?.primaryInterests || formData?.interests,
        currentItinerary: currentPlan || null,
      });

      setAgentResponse(response);

      // If a valid itinerary was produced or updated by agent, update parent plan
      if (response.itinerary && onPlanUpdated) {
        onPlanUpdated(response.itinerary);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to execute agent request');
    } finally {
      setIsLoading(false);
      if (setIsAdapting) setIsAdapting(false);
    }
  };

  const handleSelectPrompt = (promptText) => {
    setUserRequest(promptText);
  };

  const isLiveConnected = agentStatus?.provider?.available === true;

  return (
    <div className="rounded-2xl border border-sand-300 bg-parchment-50/70 p-5 sm:p-6 shadow-subtle mb-8">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-sand-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-forest-900 text-sand-100 flex items-center justify-center shadow-subtle shrink-0">
            <Bot className="w-5 h-5 text-forest-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-serif text-lg font-bold text-forest-950">
                Strands Decider 2B Assistant
              </h3>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-sand-200/80 text-charcoal-700">
                <Cpu className="w-3 h-3 text-forest-700" />
                <span>StrandsAgents/strands-decider-2B</span>
              </span>
            </div>
            <p className="text-xs text-charcoal-600 mt-0.5">
              Autonomous tool selection and sequential travel planning orchestration via Strands SDK.
            </p>
          </div>
        </div>

        {/* Live Provider Connectivity Pill */}
        <div className="flex items-center gap-2 self-start sm:self-auto text-xs">
          <span className={`w-2 h-2 rounded-full ${isLiveConnected ? 'bg-forest-600 animate-pulse' : 'bg-amber-500'}`} />
          <span className="text-charcoal-600 font-medium">
            Inference Backend: {isLiveConnected ? 'Live Server Connected' : 'Endpoint Offline'}
          </span>
        </div>
      </div>

      {/* Natural Language Prompt Input */}
      <form onSubmit={handleSubmit} className="mt-4">
        <label htmlFor="agent-prompt" className="block text-xs font-semibold text-charcoal-800 uppercase tracking-wider mb-2">
          Natural-Language Planning Instruction
        </label>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              id="agent-prompt"
              type="text"
              value={userRequest}
              onChange={(e) => setUserRequest(e.target.value)}
              placeholder="e.g., Shorten my trip to 2 days, cut costs to ₹15,000, and focus on heritage..."
              disabled={isLoading || isAdapting}
              className="w-full rounded-xl border border-sand-300 bg-white px-4 py-3 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:border-forest-600 focus:outline-none focus:ring-2 focus:ring-forest-600/20 shadow-subtle disabled:bg-sand-100"
            />
          </div>
          <button
            type="submit"
            disabled={!userRequest.trim() || isLoading || isAdapting}
            className="px-5 py-3 rounded-xl bg-forest-800 text-white font-medium text-sm hover:bg-forest-900 transition-colors shadow-subtle disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shrink-0"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Decider Thinking...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ask Decider 2B</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="mt-3 flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-medium text-charcoal-500 mr-1">Suggestions:</span>
          {PRESET_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPrompt(prompt)}
              disabled={isLoading || isAdapting}
              className="px-2.5 py-1 rounded-lg text-xs bg-sand-200/60 hover:bg-sand-200 text-charcoal-700 border border-sand-300/60 transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
      </form>

      {/* Error Banner */}
      {errorMessage && (
        <div className="mt-4 rounded-xl border border-red-300 bg-red-50/80 p-3.5 flex items-start gap-2.5 text-xs text-red-800">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
          <div className="flex-1">{errorMessage}</div>
        </div>
      )}

      {/* Agent Response & Execution Details */}
      {agentResponse && (
        <div className="mt-5 pt-5 border-t border-sand-200 space-y-4">
          {/* Status Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                agentResponse.status === 'success'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-amber-100 text-amber-900 border border-amber-300'
              }`}>
                {agentResponse.status === 'success' ? 'Autonomous Execution Complete' : 'Provider Offline'}
              </span>
              <span className="text-xs text-charcoal-500">
                Mode: <code className="font-mono">{agentResponse.execution_mode}</code>
              </span>
            </div>

            {agentResponse.tool_traces?.length > 0 && (
              <button
                type="button"
                onClick={() => setShowTraces(!showTraces)}
                className="text-xs text-forest-700 hover:text-forest-900 font-medium inline-flex items-center gap-1"
              >
                <span>{showTraces ? 'Hide Tool Traces' : `View ${agentResponse.tool_traces.length} Tool Trace(s)`}</span>
                {showTraces ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          {/* Explanation Text */}
          <div className="rounded-xl bg-white border border-sand-200 p-4 shadow-subtle">
            <p className="text-xs sm:text-sm text-charcoal-800 leading-relaxed font-sans">
              {agentResponse.explanation}
            </p>

            {/* If provider is offline, show setup command banner */}
            {agentResponse.status === 'provider_unavailable' && (
              <div className="mt-3 pt-3 border-t border-sand-200">
                <div className="text-[11px] font-semibold text-charcoal-700 mb-1 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-forest-700" />
                  <span>Launch Decider 2B Server for Genuine Live Inferences:</span>
                </div>
                <div className="bg-charcoal-900 text-sand-100 p-2.5 rounded-lg text-xs font-mono select-all overflow-x-auto">
                  strands-decider serve {agentResponse.model} --port 8001
                </div>
              </div>
            )}
          </div>

          {/* Selected Tools & Confidence Badges */}
          {agentResponse.selected_tools?.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-medium text-charcoal-600">Selected Tools:</span>
              {agentResponse.selected_tools.map((toolName, idx) => {
                const trace = agentResponse.tool_traces?.find(t => t.tool_name === toolName);
                return (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-forest-50 border border-forest-200 text-forest-900"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-forest-600" />
                    <span className="font-mono">{toolName}</span>
                    {trace && (
                      <span className="text-[10px] bg-forest-200/60 px-1.5 py-0.2 rounded text-forest-800 font-mono">
                        {Math.round(trace.confidence * 100)}% conf
                      </span>
                    )}
                  </span>
                );
              })}
            </div>
          )}

          {/* Sequential Tool Execution Traces */}
          {showTraces && agentResponse.tool_traces?.length > 0 && (
            <div className="space-y-2.5">
              <div className="text-xs font-semibold uppercase tracking-wider text-charcoal-600">
                Sequential Decision Trace
              </div>
              <div className="space-y-2">
                {agentResponse.tool_traces.map((trace, idx) => (
                  <div
                    key={idx}
                    className="rounded-xl border border-sand-200 bg-white/90 p-3.5 text-xs text-charcoal-800 shadow-subtle"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="font-semibold text-forest-900 flex items-center gap-1.5">
                        <span className="w-5 h-5 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center text-[10px] font-bold">
                          {trace.step}
                        </span>
                        <code className="font-mono">{trace.tool_name}</code>
                      </span>
                      <span className="font-mono text-[11px] text-charcoal-500">
                        Confidence: {(trace.confidence * 100).toFixed(1)}%
                      </span>
                    </div>

                    <p className="text-xs text-charcoal-600 mt-1">
                      {trace.output_summary}
                    </p>

                    {/* Probabilities breakdown */}
                    {trace.probabilities && Object.keys(trace.probabilities).length > 0 && (
                      <div className="mt-2 pt-2 border-t border-sand-100 flex items-center gap-3 flex-wrap text-[11px] text-charcoal-500">
                        <span className="font-medium text-charcoal-700">Probabilities:</span>
                        {Object.entries(trace.probabilities).map(([opt, prob]) => (
                          <span key={opt} className="font-mono">
                            {opt}: {(prob * 100).toFixed(1)}%
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
