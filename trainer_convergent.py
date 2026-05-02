#!/usr/bin/env python3
"""
Convergent Trainer for AI-Agent - Improved training with better convergence.

Key improvements for convergence:
1. Direct code modification based on failure analysis
2. Immediate testing of updated agent
3. Progressive learning with memory of changes
4. Specific, actionable improvements targeting exact failure points
5. Success rate tracking across iterations
"""

import json
import os
import sys
import time
import copy
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from conversation_runner import run_all_simulations
from ollama_integration import OllamaClient


class ConvergentTrainer:
    """Improved trainer with better convergence through direct code modification."""
    
    def __init__(self, llm_model: str = "minimax-m2.5:cloud"):
        """
        Initialize the convergent trainer.
        
        Args:
            llm_model: Ollama model to use
        """
        self.llm_model = llm_model
        self.llm_client = OllamaClient(model=llm_model)
        self.agent_file = "agent/banking_agent.py"
        self.training_logs_dir = "convergent_training_logs"
        self.convergence_history = []
        
        # Create training logs directory
        os.makedirs(self.training_logs_dir, exist_ok=True)
        
    def run_convergent_training(self, max_iterations: int = 10, 
                               target_success_rate: float = 0.9,
                               max_messages: int = 10) -> Dict[str, Any]:
        """
        Run convergent training until success rate target or max iterations.
        
        Args:
            max_iterations: Maximum training iterations
            target_success_rate: Target success rate (0.0 to 1.0)
            max_messages: Maximum messages per conversation
            
        Returns:
            Training results
        """
        print("="*60)
        print("CONVERGENT TRAINING")
        print("="*60)
        print(f"Target success rate: {target_success_rate*100:.1f}%")
        print(f"Max iterations: {max_iterations}")
        print(f"Max messages per conversation: {max_messages}")
        print("="*60)
        
        iteration = 0
        current_success_rate = 0.0
        best_success_rate = 0.0
        best_agent_state = None
        
        while iteration < max_iterations and current_success_rate < target_success_rate:
            iteration += 1
            print(f"\n{'='*40}")
            print(f"ITERATION {iteration}/{max_iterations}")
            print(f"{'='*40}")
            
            # Step 1: Run simulations with current agent
            print("\n1. Testing current agent...")
            all_results = run_all_simulations(max_messages=max_messages)
            
            # Step 2: Calculate success rate
            success_rate, analysis = self._calculate_success_rate(all_results)
            current_success_rate = success_rate
            
            print(f"   Success rate: {success_rate*100:.1f}% ({analysis['successful']}/{analysis['total']})")
            
            # Save best agent state
            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_agent_state = self._backup_agent_state(iteration)
                print(f"   New best success rate! (Saved backup)")
            
            # Check if target reached
            if success_rate >= target_success_rate:
                print(f"\n✓ Target success rate of {target_success_rate*100:.1f}% achieved!")
                break
            
            # Step 3: Analyze specific failures
            print("\n2. Analyzing failures...")
            failure_analysis = self._analyze_specific_failures(all_results, analysis)
            
            # Step 4: Generate targeted fixes
            print("\n3. Generating targeted fixes...")
            fixes = self._generate_targeted_fixes(failure_analysis, iteration)
            
            # Step 5: Apply fixes to agent code
            print("\n4. Applying fixes to agent code...")
            applied = self._apply_agent_fixes(fixes)
            
            if not applied:
                print("   No fixes could be applied. Trying alternative approach...")
                # Try a different approach
                fixes = self._generate_alternative_fixes(failure_analysis, iteration)
                applied = self._apply_agent_fixes(fixes)
            
            # Step 6: Save iteration results
            iteration_results = self._save_iteration_results(
                iteration, all_results, analysis, failure_analysis, fixes, applied, success_rate
            )
            
            self.convergence_history.append(iteration_results)
            
            # Brief pause between iterations
            if iteration < max_iterations and current_success_rate < target_success_rate:
                print(f"\nPausing before next iteration...")
                time.sleep(2)
        
        # Final summary
        final_results = self._generate_final_summary()
        
        # Restore best agent if final iteration is worse
        if best_agent_state and current_success_rate < best_success_rate:
            print(f"\nRestoring best agent (success rate: {best_success_rate*100:.1f}%)...")
            self._restore_agent_state(best_agent_state)
        
        return final_results
    
    def _calculate_success_rate(self, all_results: Dict[str, Dict[str, Any]]) -> Tuple[float, Dict[str, int]]:
        """Calculate success rate from simulation results."""
        total = 0
        successful = 0
        unsuccessful = 0
        errors = 0
        
        for sim_name, results in all_results.items():
            total += 1
            if "error" in results:
                errors += 1
            elif results.get("outcome") == "SUCCESSFUL":
                successful += 1
            else:
                unsuccessful += 1
        
        success_rate = successful / max(total, 1)
        
        analysis = {
            "total": total,
            "successful": successful,
            "unsuccessful": unsuccessful,
            "errors": errors
        }
        
        return success_rate, analysis
    
    def _analyze_specific_failures(self, all_results: Dict[str, Any], 
                                  analysis: Dict[str, int]) -> Dict[str, Any]:
        """Analyze specific failure points in conversations."""
        failure_analysis = {
            "failed_simulations": [],
            "failure_patterns": {},
            "specific_issues": []
        }
        
        # Common failure patterns to look for
        failure_patterns = {
            "max_messages_reached": "Conversation reached maximum messages",
            "bill_number_not_extracted": "Agent failed to extract bill number",
            "off_topic_not_detected": "Agent failed to detect off-topic question",
            "wrong_tool_used": "Agent used wrong tool for the situation",
            "no_tool_used": "Agent didn't use tool when it should have",
            "clarification_missing": "Agent didn't ask for clarification when needed",
            "incorrect_response": "Agent gave incorrect or irrelevant response"
        }
        
        for sim_name, results in all_results.items():
            if "error" in results or results.get("outcome") == "SUCCESSFUL":
                continue
            
            # Analyze this failed conversation
            conversation = results.get("conversation_history", [])
            failure_reason = results.get("success_reason", "")
            
            # Detect specific failure patterns
            detected_patterns = []
            
            if "maximum" in failure_reason.lower() and "messages" in failure_reason.lower():
                detected_patterns.append("max_messages_reached")
            
            # Check conversation content for patterns
            conversation_text = " ".join([msg.get("content", "").lower() for msg in conversation])
            
            if "bill" in conversation_text and "number" in conversation_text:
                if "inv-" in conversation_text or "bill-" in conversation_text:
                    # Bill number was mentioned but agent didn't use check_bill_status
                    if "tool: check_bill_status" not in str(conversation).lower():
                        detected_patterns.append("bill_number_not_extracted")
            
            if "weather" in conversation_text or "rain" in conversation_text or "sunny" in conversation_text:
                if "not my question" not in conversation_text:
                    detected_patterns.append("off_topic_not_detected")
            
            # Check tool usage patterns
            tools_used = results.get("tools_used", {})
            if not tools_used:
                detected_patterns.append("no_tool_used")
            
            failed_sim = {
                "simulation": sim_name,
                "reason": failure_reason,
                "patterns": detected_patterns,
                "conversation_length": len(conversation),
                "tools_used": list(tools_used.keys())
            }
            
            failure_analysis["failed_simulations"].append(failed_sim)
            
            # Update pattern counts
            for pattern in detected_patterns:
                failure_analysis["failure_patterns"][pattern] = failure_analysis["failure_patterns"].get(pattern, 0) + 1
        
        # Generate specific issues from patterns
        for pattern, count in failure_analysis["failure_patterns"].items():
            if pattern in failure_patterns:
                failure_analysis["specific_issues"].append({
                    "issue": failure_patterns[pattern],
                    "pattern": pattern,
                    "count": count,
                    "priority": "HIGH" if count > 1 else "MEDIUM"
                })
        
        return failure_analysis
    
    def _generate_targeted_fixes(self, failure_analysis: Dict[str, Any], 
                                iteration: int) -> Dict[str, Any]:
        """Generate targeted fixes for specific failure patterns."""
        print("   Consulting LLM for targeted fixes...")
        
        # Prepare focused prompt based on specific failures
        prompt = self._create_targeted_fix_prompt(failure_analysis, iteration)
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt="You are an expert Python developer specializing in AI agent code. Provide specific, actionable code changes.",
                temperature=0.2,
                max_tokens=2000
            )
            
            fixes = self._parse_fix_response(response, failure_analysis)
            return fixes
            
        except Exception as e:
            print(f"   Error generating fixes: {e}")
            return {"error": str(e), "fixes": []}
    
    def _create_targeted_fix_prompt(self, failure_analysis: Dict[str, Any], 
                                   iteration: int) -> str:
        """Create a prompt for targeted fixes."""
        # Read current agent code
        try:
            with open(self.agent_file, 'r') as f:
                current_code = f.read()
        except FileNotFoundError:
            current_code = "Agent code file not found."
        
        # Build prompt focusing on specific issues
        prompt = f"""You are fixing a banking AI agent that has the following issues:

CURRENT AGENT CODE:
{current_code[:3000]}  # Truncated for brevity

FAILURE ANALYSIS (Iteration {iteration}):
"""
        
        for issue in failure_analysis.get("specific_issues", []):
            prompt += f"- {issue['issue']} (Priority: {issue['priority']}, Count: {issue['count']})\n"
        
        prompt += f"""
FAILURE PATTERNS DETECTED:
"""
        
        for pattern, count in failure_analysis.get("failure_patterns", {}).items():
            prompt += f"- {pattern}: {count} occurrence(s)\n"
        
        prompt += """
REQUIRED FIXES:
Please provide SPECIFIC Python code changes to fix these issues. Focus on:

1. **Bill number extraction**: Improve regex patterns or add more bill number formats
2. **Off-topic detection**: Enhance keyword matching or add more off-topic categories  
3. **Tool selection logic**: Fix when to use check_bill_status vs provide_bank_information
4. **Clarification questions**: Add missing clarification prompts
5. **Response relevance**: Ensure responses directly address user queries

Provide your response in this EXACT format:
ISSUE: [Brief description of the issue]
CODE_LOCATION: [Class.method or function name]
CURRENT_CODE: [Exact code snippet that needs changing]
PROPOSED_CHANGE: [Exact new code snippet]
REASON: [Why this change addresses the issue]

Provide as many fixes as needed, one per section.
"""
        
        return prompt
    
    def _parse_fix_response(self, response: str, failure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response to extract specific code fixes."""
        fixes = {
            "raw_response": response,
            "parsed_fixes": [],
            "summary": ""
        }
        
        # Simple parsing - look for ISSUE: patterns
        sections = response.split("ISSUE:")
        
        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            fix = {
                "issue": lines[0].strip(),
                "code_location": "",
                "current_code": "",
                "proposed_change": "",
                "reason": ""
            }
            
            current_field = None
            current_content = []
            
            for line in lines[1:]:
                line_lower = line.lower()
                
                if "code_location:" in line_lower:
                    current_field = "code_location"
                    fix["code_location"] = line.replace("CODE_LOCATION:", "").strip()
                elif "current_code:" in line_lower:
                    current_field = "current_code"
                    fix["current_code"] = line.replace("CURRENT_CODE:", "").strip()
                elif "proposed_change:" in line_lower:
                    current_field = "proposed_change"
                    fix["proposed_change"] = line.replace("PROPOSED_CHANGE:", "").strip()
                elif "reason:" in line_lower:
                    current_field = "reason"
                    fix["reason"] = line.replace("REASON:", "").strip()
                elif current_field and line.strip():
                    # Append to current field
                    if current_field == "current_code":
                        fix["current_code"] += "\n" + line
                    elif current_field == "proposed_change":
                        fix["proposed_change"] += "\n" + line
                    elif current_field == "reason":
                        fix["reason"] += " " + line.strip()
            
            fixes["parsed_fixes"].append(fix)
        
        return fixes
    
    def _apply_agent_fixes(self, fixes: Dict[str, Any]) -> bool:
        """Apply fixes to the agent code file."""
        if "error" in fixes or not fixes.get("parsed_fixes"):
            print("   No valid fixes to apply.")
            return False
        
        try:
            # Read current agent code
            with open(self.agent_file, 'r') as f:
                current_code = f.read()
            
            # Create backup
            backup_file = f"{self.agent_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w') as f:
                f.write(current_code)
            
            updated_code = current_code
            applied_count = 0
            
            # Apply each fix
            for fix in fixes["parsed_fixes"]:
                current_snippet = fix.get("current_code", "").strip()
                proposed_snippet = fix.get("proposed_change", "").strip()
                
                if current_snippet and proposed_snippet and current_snippet in updated_code:
                    # Apply the fix
                    updated_code = updated_code.replace(current_snippet, proposed_snippet)
                    applied_count += 1
                    print(f"   Applied fix: {fix.get('issue', 'Unknown')}")
                else:
                    print(f"   Could not apply fix: {fix.get('issue', 'Unknown')}")
                    print(f"     Current snippet not found or empty")
            
            # Write updated code
            if applied_count > 0:
                with open(self.agent_file, 'w') as f:
                    f.write(updated_code)
                print(f"   Applied {applied_count} fix(es) to agent code.")
                return True
            else:
                print("   No fixes could be applied (code snippets not found).")
                # Restore backup
                with open(self.agent_file, 'w') as f:
                    f.write(current_code)
                return False
                
        except Exception as e:
            print(f"   Error applying fixes: {e}")
            return False
    
    def _generate_alternative_fixes(self, failure_analysis: Dict[str, Any], 
                                   iteration: int) -> Dict[str, Any]:
        """Generate alternative fixes when primary approach fails."""
        print("   Trying alternative fix generation...")
        
        # Simple rule-based fixes as fallback
        fixes = {
            "raw_response": "Alternative rule-based fixes",
            "parsed_fixes": [],
            "summary": "Rule-based fixes based on failure patterns"
        }
        
        # Generate simple fixes based on common patterns
        for pattern, count in failure_analysis.get("failure_patterns", {}).items():
            if pattern == "bill_number_not_extracted":
                fix = {
                    "issue": "Agent fails to extract bill numbers",
                    "code_location": "BankingAgentImpl.extract_bill_number",
                    "current_code": "    BILL_PATTERNS = [\n        r'INV-\\d{4}-\\d{3}',  # INV-2024-001\n        r'BILL-\\d{6}',        # BILL-123456\n        r'\\d{10}',            # 1234567890\n        r'[A-Z]{3}-\\d{5}',    # ABC-12345\n    ]",
                    "proposed_change": "    BILL_PATTERNS = [\n        r'INV-\\d{4}-\\d{3}',  # INV-2024-001\n        r'BILL-\\d{6}',        # BILL-123456\n        r'\\d{10}',            # 1234567890\n        r'[A-Z]{3}-\\d{5}',    # ABC-12345\n        r'INV\\d{8}',          # INV20240001\n        r'BL-\\d{4}-\\d{4}',   # BL-2024-0001\n    ]",
                    "reason": "Add more bill number patterns to improve extraction"
                }
                fixes["parsed_fixes"].append(fix)
            
            elif pattern == "off_topic_not_detected":
                fix = {
                    "issue": "Agent fails to detect off-topic weather questions",
                    "code_location": "BankingAgentImpl.is_off_topic",
                    "current_code": "        off_topic_indicators = [\n            'weather', 'sports', 'movie', 'music', 'tv', 'entertainment',\n            'recipe', 'cooking', 'travel', 'vacation', 'holiday', 'party',\n            'medical', 'health', 'doctor', 'hospital', 'medicine',\n            'legal', 'lawyer', 'court', 'lawsuit',\n            'political', 'election', 'government', 'president',\n            'technical', 'computer', 'software', 'hardware', 'internet',\n            'relationship', 'family', 'friend', 'dating',\n            'joke', 'funny', 'humor', 'comedy'\n        ]",
                    "proposed_change": "        off_topic_indicators = [\n            'weather', 'forecast', 'rain', 'sunny', 'cloud', 'temperature', 'sports', 'movie', 'music', 'tv', 'entertainment',\n            'recipe', 'cooking', 'travel', 'vacation', 'holiday', 'party',\n            'medical', 'health', 'doctor', 'hospital', 'medicine',\n            'legal', 'lawyer', 'court', 'lawsuit',\n            'political', 'election', 'government', 'president',\n            'technical', 'computer', 'software', 'hardware', 'internet',\n            'relationship', 'family', 'friend', 'dating',\n            'joke', 'funny', 'humor', 'comedy'\n        ]",
                    "reason": "Add more weather-related keywords for better off-topic detection"
                }
                fixes["parsed_fixes"].append(fix)
        
        return fixes
    
    def _backup_agent_state(self, iteration: int) -> Dict[str, Any]:
        """Backup current agent state."""
        try:
            with open(self.agent_file, 'r') as f:
                agent_code = f.read()
            
            backup = {
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(),
                "agent_code": agent_code,
                "backup_file": f"{self.training_logs_dir}/agent_backup_iteration_{iteration}.py"
            }
            
            # Save backup file
            with open(backup["backup_file"], 'w') as f:
                f.write(agent_code)
            
            return backup
        except Exception as e:
            print(f"   Error backing up agent state: {e}")
            return None
    
    def _restore_agent_state(self, backup_state: Dict[str, Any]) -> bool:
        """Restore agent from backup state."""
        try:
            if backup_state and "agent_code" in backup_state:
                with open(self.agent_file, 'w') as f:
                    f.write(backup_state["agent_code"])
                print(f"   Agent restored from iteration {backup_state.get('iteration', 'unknown')}")
                return True
        except Exception as e:
            print(f"   Error restoring agent state: {e}")
        
        return False
    
    def _save_iteration_results(self, iteration: int, all_results: Dict[str, Any],
                               analysis: Dict[str, int], failure_analysis: Dict[str, Any],
                               fixes: Dict[str, Any], applied: bool, success_rate: float) -> Dict[str, Any]:
        """Save iteration results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.training_logs_dir, f"iteration_{iteration}_{timestamp}.json")
        
        iteration_results = {
            "iteration": iteration,
            "timestamp": timestamp,
            "success_rate": success_rate,
            "analysis": analysis,
            "failure_analysis": failure_analysis,
            "fixes_applied": applied,
            "fixes_generated": len(fixes.get("parsed_fixes", [])),
            "fixes_summary": fixes.get("summary", "")
        }
        
        with open(results_file, 'w') as f:
            json.dump(iteration_results, f, indent=2)
        
        print(f"   Iteration results saved to: {results_file}")
        
        return iteration_results
    
    def _generate_final_summary(self) -> Dict[str, Any]:
        """Generate final training summary."""
        if not self.convergence_history:
            return {"error": "No training iterations completed"}
        
        initial_success = self.convergence_history[0]["success_rate"] if self.convergence_history else 0
        final_success = self.convergence_history[-1]["success_rate"] if self.convergence_history else 0
        improvement = final_success - initial_success
        
        summary = {
            "total_iterations": len(self.convergence_history),
            "initial_success_rate": initial_success,
            "final_success_rate": final_success,
            "improvement": improvement,
            "improvement_percentage": (improvement / max(initial_success, 0.01)) * 100 if initial_success > 0 else 0,
            "converged": improvement > 0.1 or final_success > 0.8,  # Simple convergence criteria
            "iterations": self.convergence_history
        }
        
        # Save summary
        summary_file = os.path.join(self.training_logs_dir, "training_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        print(f"Total iterations: {summary['total_iterations']}")
        print(f"Initial success rate: {initial_success*100:.1f}%")
        print(f"Final success rate: {final_success*100:.1f}%")
        print(f"Improvement: {improvement*100:+.1f}% ({summary['improvement_percentage']:.1f}% relative)")
        print(f"Converged: {'✓ YES' if summary['converged'] else '✗ NO'}")
        print("="*60)
        
        return summary


def main():
    """Main entry point for convergent trainer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convergent Trainer - Improve agent with better convergence"
    )
    
    parser.add_argument("--iterations", "-i", type=int, default=5,
                       help="Maximum training iterations (default: 5)")
    parser.add_argument("--target", "-t", type=float, default=0.9,
                       help="Target success rate (0.0 to 1.0, default: 0.9)")
    parser.add_argument("--max-messages", "-m", type=int, default=10,
                       help="Maximum messages per conversation (default: 10)")
    parser.add_argument("--model", type=str, default="minimax-m2.5:cloud",
                       help="Ollama model to use (default: minimax-m2.5:cloud)")
    
    args = parser.parse_args()
    
    print("CONVERGENT TRAINER")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Max iterations: {args.iterations}")
    print(f"Target success rate: {args.target*100:.1f}%")
    print(f"Max messages: {args.max_messages}")
    print("="*60)
    
    # Check if Ollama is available
    client = OllamaClient(model=args.model)
    if not client.check_model_available():
        print(f"\nError: Model '{args.model}' is not available.")
        print("Please pull it with: ollama pull minimax-m2.5:cloud")
        return 1
    
    # Create and run trainer
    trainer = ConvergentTrainer(llm_model=args.model)
    results = trainer.run_convergent_training(
        max_iterations=args.iterations,
        target_success_rate=args.target,
        max_messages=args.max_messages
    )
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)