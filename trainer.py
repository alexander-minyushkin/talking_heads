#!/usr/bin/env python3
"""
AI-Agent Trainer Script

Runs all available simulations and if dialogues are unsuccessful,
updates the Agent skill by requesting improvements from LLM
given the examples and recommendations.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from conversation_runner import run_all_simulations
from ollama_integration import OllamaClient


class AgentTrainer:
    """Trains the banking agent by analyzing unsuccessful conversations."""
    
    def __init__(self, llm_model: str = "minimax-m2.5:cloud"):
        """
        Initialize the trainer.
        
        Args:
            llm_model: Ollama model to use for skill improvement
        """
        self.llm_model = llm_model
        self.llm_client = OllamaClient(model=llm_model)
        self.agent_skill_file = "agent/banking_agent_skill.md"
        self.training_logs_dir = "training_logs"
        
        # Create training logs directory
        os.makedirs(self.training_logs_dir, exist_ok=True)
        
    def run_training_cycle(self, max_messages: int = 10) -> Dict[str, Any]:
        """
        Run a complete training cycle.
        
        Args:
            max_messages: Maximum messages per conversation
            
        Returns:
            Training results summary
        """
        print("="*60)
        print("AI-AGENT TRAINING CYCLE")
        print("="*60)
        
        # Step 1: Run all simulations
        print("\n1. Running all simulations...")
        all_results = run_all_simulations(max_messages=max_messages)
        
        # Step 2: Analyze results
        print("\n2. Analyzing simulation results...")
        analysis = self.analyze_results(all_results)
        
        # Step 3: Check if improvements are needed
        if analysis["unsuccessful_count"] > 0:
            print(f"\n3. Found {analysis['unsuccessful_count']} unsuccessful simulations.")
            print("   Generating improvements...")
            
            # Step 4: Generate improvements using LLM
            improvements = self.generate_improvements(analysis)
            
            # Step 5: Update agent skill
            print("\n4. Updating agent skill...")
            updated = self.update_agent_skill(improvements)
            
            if updated:
                print("   Agent skill updated successfully.")
            else:
                print("   Failed to update agent skill.")
        else:
            print("\n3. All simulations successful! No improvements needed.")
            improvements = {}
            updated = False
        
        # Step 6: Save training results
        print("\n5. Saving training results...")
        training_results = self.save_training_results(
            all_results, analysis, improvements, updated
        )
        
        print("\n" + "="*60)
        print("TRAINING CYCLE COMPLETE")
        print("="*60)
        
        return training_results
    
    def analyze_results(self, all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze simulation results to identify patterns and issues.
        
        Args:
            all_results: Results from all simulations
            
        Returns:
            Analysis dictionary
        """
        analysis = {
            "total_simulations": len(all_results),
            "successful_count": 0,
            "unsuccessful_count": 0,
            "errors_count": 0,
            "unsuccessful_simulations": [],
            "common_issues": [],
            "conversation_patterns": []
        }
        
        for sim_name, results in all_results.items():
            if "error" in results:
                analysis["errors_count"] += 1
                continue
            
            outcome = results.get("outcome", "UNKNOWN")
            if outcome == "SUCCESSFUL":
                analysis["successful_count"] += 1
            else:
                analysis["unsuccessful_count"] += 1
                
                # Collect details about unsuccessful simulation
                unsuccessful_info = {
                    "simulation": sim_name,
                    "human_goal": results.get("human_goal", "Unknown"),
                    "success_reason": results.get("success_reason", "Unknown"),
                    "total_messages": results.get("total_messages", 0),
                    "max_messages": results.get("max_messages", 10),
                    "conversation_excerpt": self._extract_conversation_excerpt(results)
                }
                analysis["unsuccessful_simulations"].append(unsuccessful_info)
        
        # Analyze common issues
        analysis["common_issues"] = self._identify_common_issues(analysis["unsuccessful_simulations"])
        
        return analysis
    
    def _extract_conversation_excerpt(self, results: Dict[str, Any], max_lines: int = 5) -> str:
        """Extract a conversation excerpt for analysis."""
        history = results.get("conversation_history", [])
        if not history:
            return "No conversation history available."
        
        excerpt = []
        for i, msg in enumerate(history[:max_lines]):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            tool = msg.get("tool", "")
            
            tool_info = f" [Tool: {tool}]" if tool else ""
            excerpt.append(f"{role}{tool_info}: {content}")
        
        return "\n".join(excerpt)
    
    def _identify_common_issues(self, unsuccessful_sims: List[Dict[str, Any]]) -> List[str]:
        """Identify common issues from unsuccessful simulations."""
        issues = []
        
        for sim in unsuccessful_sims:
            reason = sim.get("success_reason", "").lower()
            excerpt = sim.get("conversation_excerpt", "").lower()
            
            # Check for specific issues
            if "maximum" in reason and "messages" in reason:
                issues.append("Conversation exceeded maximum message limit")
            
            if "bill" in excerpt and "number" in excerpt and "not" in excerpt:
                issues.append("Agent failed to extract or use bill number")
            
            if "weather" in excerpt and "not my question" not in excerpt:
                issues.append("Agent failed to detect off-topic weather question")
            
            if "mortgage" in excerpt and "rate" in excerpt and "information" not in excerpt:
                issues.append("Agent failed to provide mortgage rate information")
        
        # Deduplicate issues
        return list(set(issues))
    
    def generate_improvements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate improvements for the agent skill using LLM.
        
        Args:
            analysis: Analysis of simulation results
            
        Returns:
            Improvements dictionary
        """
        # Prepare prompt for LLM
        prompt = self._create_improvement_prompt(analysis)
        
        print("   Consulting LLM for improvements...")
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt="You are an expert AI agent trainer specializing in banking chatbots.",
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the response
            improvements = self._parse_llm_response(response)
            
            return improvements
            
        except Exception as e:
            print(f"   Error generating improvements: {e}")
            return {
                "error": str(e),
                "recommendations": ["Check LLM connection and try again."]
            }
    
    def _create_improvement_prompt(self, analysis: Dict[str, Any]) -> str:
        """Create a prompt for LLM to generate improvements."""
        # Read current agent skill
        try:
            with open(self.agent_skill_file, 'r') as f:
                current_skill = f.read()
        except FileNotFoundError:
            current_skill = "Agent skill file not found."
        
        # Build prompt
        prompt = f"""As an expert AI agent trainer, analyze the following simulation results and suggest improvements to the banking agent skill.

CURRENT AGENT SKILL:
{current_skill}

SIMULATION ANALYSIS:
- Total simulations: {analysis['total_simulations']}
- Successful: {analysis['successful_count']}
- Unsuccessful: {analysis['unsuccessful_count']}
- Errors: {analysis['errors_count']}

UNSUCCESSFUL SIMULATIONS:
"""
        
        for i, sim in enumerate(analysis['unsuccessful_simulations'], 1):
            prompt += f"""
{i}. Simulation: {sim['simulation']}
   Goal: {sim['human_goal']}
   Reason for failure: {sim['success_reason']}
   Conversation excerpt:
{sim['conversation_excerpt']}
"""
        
        prompt += f"""
COMMON ISSUES IDENTIFIED:
{chr(10).join(f'- {issue}' for issue in analysis['common_issues'])}

Please provide specific, actionable improvements to the agent skill document. Focus on:
1. Tool usage improvements (when to use check_bill_status vs provide_bank_information)
2. Better off-topic detection
3. Clarification question improvements
4. Conversation flow enhancements
5. Any missing banking topics or edge cases

Format your response as:
IMPROVEMENTS SUMMARY: [Brief summary]
SPECIFIC CHANGES: [List of specific changes to make]
UPDATED SKILL SECTIONS: [Provide updated sections if needed]
"""

        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract improvements."""
        improvements = {
            "summary": "",
            "specific_changes": [],
            "updated_sections": {},
            "raw_response": response
        }
        
        # Simple parsing - in a real implementation, this would be more sophisticated
        lines = response.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower()
            
            if "improvements summary:" in line_lower:
                current_section = "summary"
                improvements["summary"] = line.replace("IMPROVEMENTS SUMMARY:", "").strip()
            elif "specific changes:" in line_lower:
                current_section = "specific_changes"
            elif "updated skill sections:" in line_lower:
                current_section = "updated_sections"
            elif current_section == "specific_changes" and line.strip().startswith("-"):
                improvements["specific_changes"].append(line.strip()[1:].strip())
            elif current_section == "summary" and improvements["summary"]:
                improvements["summary"] += " " + line.strip()
        
        return improvements
    
    def update_agent_skill(self, improvements: Dict[str, Any]) -> bool:
        """
        Update the agent skill file with improvements.
        
        Args:
            improvements: Improvements generated by LLM
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Read current skill
            with open(self.agent_skill_file, 'r') as f:
                current_content = f.read()
            
            # Create backup
            backup_file = f"{self.agent_skill_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w') as f:
                f.write(current_content)
            
            # Generate updated content using LLM
            update_prompt = f"""Update the following banking agent skill document with these improvements:

CURRENT SKILL DOCUMENT:
{current_content}

IMPROVEMENTS TO INCORPORATE:
Summary: {improvements.get('summary', 'No summary provided')}

Specific Changes:
{chr(10).join(f'- {change}' for change in improvements.get('specific_changes', []))}

Please provide the COMPLETE updated skill document with all improvements incorporated.
Maintain the same markdown format and structure.
"""
            
            print("   Generating updated skill document...")
            updated_content = self.llm_client.generate(
                prompt=update_prompt,
                system_prompt="You are a technical writer specializing in AI agent documentation.",
                temperature=0.2,
                max_tokens=2000
            )
            
            # Write updated content
            with open(self.agent_skill_file, 'w') as f:
                f.write(updated_content)
            
            # Also save the improvements for reference
            improvements_file = os.path.join(
                self.training_logs_dir,
                f"improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(improvements_file, 'w') as f:
                json.dump(improvements, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"   Error updating agent skill: {e}")
            return False
    
    def save_training_results(self, all_results: Dict[str, Any], analysis: Dict[str, Any],
                             improvements: Dict[str, Any], updated: bool) -> Dict[str, Any]:
        """
        Save training results to file.
        
        Args:
            all_results: Results from all simulations
            analysis: Analysis of results
            improvements: Generated improvements
            updated: Whether agent skill was updated
            
        Returns:
            Training results summary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.training_logs_dir, f"training_results_{timestamp}.json")
        
        training_results = {
            "timestamp": timestamp,
            "training_cycle": {
                "simulations_run": len(all_results),
                "successful": analysis["successful_count"],
                "unsuccessful": analysis["unsuccessful_count"],
                "errors": analysis["errors_count"],
                "skill_updated": updated
            },
            "analysis": analysis,
            "improvements": improvements,
            "all_results": all_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(training_results, f, indent=2)
        
        print(f"   Training results saved to: {results_file}")
        
        return training_results
    
    def run_iterative_training(self, cycles: int = 3, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Run multiple training cycles iteratively.
        
        Args:
            cycles: Number of training cycles to run
            max_messages: Maximum messages per conversation
            
        Returns:
            List of training results for each cycle
        """
        all_cycle_results = []
        
        print("="*60)
        print(f"ITERATIVE TRAINING - {cycles} CYCLES")
        print("="*60)
        
        for cycle in range(1, cycles + 1):
            print(f"\n{'='*40}")
            print(f"TRAINING CYCLE {cycle}/{cycles}")
            print(f"{'='*40}")
            
            cycle_results = self.run_training_cycle(max_messages=max_messages)
            all_cycle_results.append(cycle_results)
            
            # Brief pause between cycles
            if cycle < cycles:
                print(f"\nPausing before next cycle...")
                time.sleep(2)
        
        # Generate final summary
        self._generate_training_summary(all_cycle_results)
        
        return all_cycle_results
    
    def _generate_training_summary(self, all_cycle_results: List[Dict[str, Any]]) -> None:
        """Generate and print a summary of all training cycles."""
        print("\n" + "="*60)
        print("ITERATIVE TRAINING SUMMARY")
        print("="*60)
        
        for i, results in enumerate(all_cycle_results, 1):
            cycle_info = results.get("training_cycle", {})
            print(f"\nCycle {i}:")
            print(f"  Simulations: {cycle_info.get('simulations_run', 0)}")
            print(f"  Successful: {cycle_info.get('successful', 0)}")
            print(f"  Unsuccessful: {cycle_info.get('unsuccessful', 0)}")
            print(f"  Skill updated: {cycle_info.get('skill_updated', False)}")
        
        # Calculate improvement
        if len(all_cycle_results) > 1:
            first_cycle = all_cycle_results[0]["training_cycle"]
            last_cycle = all_cycle_results[-1]["training_cycle"]
            
            first_success_rate = first_cycle["successful"] / max(first_cycle["simulations_run"], 1)
            last_success_rate = last_cycle["successful"] / max(last_cycle["simulations_run"], 1)
            
            improvement = last_success_rate - first_success_rate
            
            print(f"\nOverall Improvement: {improvement:.2%}")
            
            if improvement > 0:
                print("✓ Training was effective!")
            else:
                print("✗ Training did not improve success rate.")


def main():
    """Main entry point for trainer script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI-Agent Trainer - Improve agent skills based on simulation results"
    )
    
    parser.add_argument("--cycles", "-c", type=int, default=1,
                       help="Number of training cycles to run (default: 1)")
    parser.add_argument("--max-messages", "-m", type=int, default=10,
                       help="Maximum messages per conversation (default: 10)")
    parser.add_argument("--model", type=str, default="minimax-m2.5:cloud",
                       help="Ollama model to use (default: minimax-m2.5:cloud)")
    
    args = parser.parse_args()
    
    print("AI-AGENT TRAINER")
    print("="*60)
    print(f"Model: {args.model}")
    print(f"Cycles: {args.cycles}")
    print(f"Max messages: {args.max_messages}")
    print("="*60)
    
    # Check if Ollama is available
    client = OllamaClient(model=args.model)
    if not client.check_model_available():
        print(f"\nError: Model '{args.model}' is not available.")
        print("Please pull it with: ollama pull minimax-m2.5:cloud")
        return 1
    
    # Create and run trainer
    trainer = AgentTrainer(llm_model=args.model)
    
    if args.cycles > 1:
        trainer.run_iterative_training(cycles=args.cycles, max_messages=args.max_messages)
    else:
        trainer.run_training_cycle(max_messages=args.max_messages)
    
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