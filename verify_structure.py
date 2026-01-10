#!/usr/bin/env python3
"""
COMPLETE PLUGIN STRUCTURE VERIFIER
Shows ALL files and directory structure for PilotFS
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

class PluginStructureVerifier:
    """Verifies and displays complete plugin structure."""
    
    def __init__(self, plugin_path: str):
        self.plugin_path = Path(plugin_path).absolute()
        self.structure = {}
        self.file_stats = {}
        self.issues = []
        self.warnings = []
        
    def verify_complete_structure(self):
        """Verify and display complete plugin structure."""
        print("=" * 80)
        print("PILOTFS COMPLETE STRUCTURE VERIFICATION")
        print("=" * 80)
        print(f"Plugin path: {self.plugin_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check if path exists
        if not self.plugin_path.exists():
            print(f"❌ ERROR: Plugin path does not exist: {self.plugin_path}")
            return False
        
        # 1. Get ALL files and directories
        print("\n📁 COMPLETE FILE STRUCTURE:")
        print("-" * 80)
        
        all_items = []
        for root, dirs, files in os.walk(self.plugin_path):
            level = root.replace(str(self.plugin_path), '').count(os.sep)
            indent = ' ' * 4 * level
            rel_path = os.path.relpath(root, self.plugin_path)
            
            if rel_path == '.':
                print(f"{indent}📦 PilotFS/")
            else:
                print(f"{indent}📁 {os.path.basename(root)}/")
            
            subindent = ' ' * 4 * (level + 1)
            
            # Sort files alphabetically
            for file in sorted(files):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                ext = os.path.splitext(file)[1]
                
                # Choose icon based on file type
                if ext == '.py':
                    icon = '🐍'
                elif ext in ['.txt', '.md', '.log']:
                    icon = '📄'
                elif ext in ['.png', '.jpg', '.gif']:
                    icon = '🖼️'
                elif ext in ['.xml', '.conf', '.cfg']:
                    icon = '⚙️'
                else:
                    icon = '📝'
                
                print(f"{subindent}{icon} {file} ({self._format_size(file_size)})")
                all_items.append(file_path)
        
        # 2. Detailed file analysis
        print("\n" + "=" * 80)
        print("📊 DETAILED FILE ANALYSIS:")
        print("-" * 80)
        
        self._analyze_files_by_type()
        
        # 3. Essential files check
        print("\n" + "=" * 80)
        print("✅ ESSENTIAL FILES CHECK:")
        print("-" * 80)
        
        self._check_essential_files()
        
        # 4. Player integration check
        print("\n" + "=" * 80)
        print("🎬 PLAYER INTEGRATION CHECK:")
        print("-" * 80)
        
        self._check_player_integration()
        
        # 5. Python files check
        print("\n" + "=" * 80)
        print("🐍 PYTHON FILES VALIDATION:")
        print("-" * 80)
        
        self._check_python_files()
        
        # 6. Compiled files cleanup status
        print("\n" + "=" * 80)
        print("🧹 COMPILED FILES CLEANUP STATUS:")
        print("-" * 80)
        
        self._check_compiled_files()
        
        # 7. Directory structure summary
        print("\n" + "=" * 80)
        print("📋 DIRECTORY STRUCTURE SUMMARY:")
        print("-" * 80)
        
        self._print_directory_summary()
        
        # 8. Issues and recommendations
        print("\n" + "=" * 80)
        print("⚠️  ISSUES & RECOMMENDATIONS:")
        print("-" * 80)
        
        self._print_issues_and_recommendations()
        
        # 9. Generate report file
        self._generate_report()
        
        print("\n" + "=" * 80)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 80)
        
        return True
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ("B", "KB", "MB", "GB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def _analyze_files_by_type(self):
        """Analyze files by type/category."""
        file_categories = {
            'Python Files': ['.py'],
            'Configuration': ['.conf', '.cfg', '.ini', '.xml', '.json'],
            'Documentation': ['.md', '.txt', '.rst'],
            'Images': ['.png', '.jpg', '.jpeg', '.gif', '.ico'],
            'Compiled': ['.pyc', '.pyo'],
            'Other': []
        }
        
        category_counts = {cat: 0 for cat in file_categories.keys()}
        category_sizes = {cat: 0 for cat in file_categories.keys()}
        
        for root, dirs, files in os.walk(self.plugin_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                ext = os.path.splitext(file)[1].lower()
                
                categorized = False
                for category, extensions in file_categories.items():
                    if ext in extensions:
                        category_counts[category] += 1
                        category_sizes[category] += file_size
                        categorized = True
                        break
                
                if not categorized:
                    category_counts['Other'] += 1
                    category_sizes['Other'] += file_size
        
        # Print analysis
        for category in file_categories.keys():
            if category_counts[category] > 0:
                print(f"{category}: {category_counts[category]} files ({self._format_size(category_sizes[category])})")
    
    def _check_essential_files(self):
        """Check for essential plugin files."""
        essential_files = {
            'CRITICAL': [
                ('plugin.py', 'Main plugin entry point'),
                ('ui/main_screen.py', 'Main user interface'),
            ],
            'IMPORTANT': [
                ('player/enigma_player.py', 'Enigma2 player implementation'),
                ('player/__init__.py', 'Player module initialization'),
                ('ui/context_menu.py', 'Context menu handler'),
                ('ui/dialogs.py', 'Dialog boxes'),
            ],
            'OPTIONAL': [
                ('core/config.py', 'Configuration manager'),
                ('core/file_operations.py', 'File operations'),
                ('network/remote_manager.py', 'Network manager'),
                ('utils/formatters.py', 'Formatting utilities'),
            ]
        }
        
        for priority, files in essential_files.items():
            print(f"\n{priority}:")
            for file_path, description in files:
                full_path = self.plugin_path / file_path
                if full_path.exists():
                    size = os.path.getsize(full_path)
                    print(f"  ✅ {file_path} - {description} ({self._format_size(size)})")
                else:
                    print(f"  ❌ {file_path} - {description} - MISSING")
                    if priority == 'CRITICAL':
                        self.issues.append(f"Missing critical file: {file_path}")
                    else:
                        self.warnings.append(f"Missing file: {file_path}")
    
    def _check_player_integration(self):
        """Check Enigma2 player integration."""
        player_files = [
            ('player/enigma_player.py', 'Main player class'),
            ('player/__init__.py', 'Module exports'),
            ('player/keymap.xml', 'Key mappings (optional)'),
        ]
        
        integration_checks = [
            ('plugin.py imports player', 'from .player.enigma_player import'),
            ('main_screen has player method', 'def play_with_enigma_player'),
            ('context_menu has player option', 'Play with Enigma2 Player'),
            ('OK button uses player', 'self.play_with_enigma_player()'),
            ('Resume points config', 'resume_points'),
        ]
        
        print("Player module files:")
        for file_path, description in player_files:
            full_path = self.plugin_path / file_path
            if full_path.exists():
                print(f"  ✅ {file_path} - {description}")
            else:
                print(f"  ❌ {file_path} - {description} - MISSING")
                self.warnings.append(f"Missing player file: {file_path}")
        
        print("\nIntegration checks:")
        for check_name, search_string in integration_checks:
            found = False
            files_checked = []
            
            # Search in relevant files
            if 'plugin.py' in check_name:
                files_to_check = ['plugin.py']
            elif 'main_screen' in check_name:
                files_to_check = ['ui/main_screen.py']
            elif 'context_menu' in check_name:
                files_to_check = ['ui/context_menu.py']
            else:
                files_to_check = ['plugin.py', 'ui/main_screen.py', 'ui/context_menu.py']
            
            for file_name in files_to_check:
                file_path = self.plugin_path / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_string in content:
                            found = True
                            files_checked.append(file_name)
            
            if found:
                print(f"  ✅ {check_name} (found in: {', '.join(files_checked)})")
            else:
                print(f"  ❌ {check_name} - NOT FOUND")
                self.warnings.append(f"Missing integration: {check_name}")
    
    def _check_python_files(self):
        """Check Python files for syntax and imports."""
        python_files = []
        syntax_errors = []
        import_errors = []
        
        # Find all Python files
        for root, dirs, files in os.walk(self.plugin_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        print(f"Found {len(python_files)} Python files")
        
        # Check a few important files
        important_files = [
            'plugin.py',
            'ui/main_screen.py',
            'player/enigma_player.py',
            'ui/context_menu.py'
        ]
        
        for file_name in important_files:
            file_path = self.plugin_path / file_name
            if file_path.exists():
                try:
                    # Try to compile (syntax check)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_name, 'exec')
                    print(f"  ✅ {file_name} - Syntax OK")
                except SyntaxError as e:
                    print(f"  ❌ {file_name} - Syntax error: {e}")
                    syntax_errors.append(f"{file_name}: {e}")
                
                # Check for obvious import issues
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for common import patterns
                        if 'import ' in content or 'from ' in content:
                            # This is a simple check, not actual import
                            pass
                except Exception as e:
                    import_errors.append(f"{file_name}: {e}")
            else:
                print(f"  ⚠  {file_name} - Not found")
        
        if syntax_errors:
            self.issues.append(f"Syntax errors found: {len(syntax_errors)}")
    
    def _check_compiled_files(self):
        """Check for leftover compiled Python files."""
        compiled_files = []
        
        for root, dirs, files in os.walk(self.plugin_path):
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    compiled_files.append(os.path.join(root, file))
            
            if '__pycache__' in dirs:
                compiled_files.append(os.path.join(root, '__pycache__'))
        
        if compiled_files:
            print(f"❌ Found {len(compiled_files)} compiled files/directories:")
            for f in compiled_files[:10]:  # Show first 10
                if os.path.isdir(f):
                    print(f"  📁 {os.path.relpath(f, self.plugin_path)}/")
                else:
                    size = os.path.getsize(f)
                    print(f"  📄 {os.path.relpath(f, self.plugin_path)} ({self._format_size(size)})")
            
            if len(compiled_files) > 10:
                print(f"  ... and {len(compiled_files) - 10} more")
            
            self.issues.append(f"Found {len(compiled_files)} compiled files - should be cleaned")
        else:
            print("✅ No compiled Python files found (good!)")
    
    def _print_directory_summary(self):
        """Print directory structure summary."""
        dirs_by_level = {}
        
        for root, dirs, files in os.walk(self.plugin_path):
            level = root.replace(str(self.plugin_path), '').count(os.sep)
            rel_path = os.path.relpath(root, self.plugin_path)
            
            if rel_path not in dirs_by_level:
                dirs_by_level[rel_path] = {
                    'level': level,
                    'file_count': 0,
                    'dir_count': 0,
                    'total_size': 0
                }
        
        # Count files and sizes
        for root, dirs, files in os.walk(self.plugin_path):
            rel_path = os.path.relpath(root, self.plugin_path)
            dirs_by_level[rel_path]['dir_count'] = len(dirs)
            dirs_by_level[rel_path]['file_count'] = len(files)
            
            total_size = 0
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
            dirs_by_level[rel_path]['total_size'] = total_size
        
        print("Directory Summary:")
        print("-" * 40)
        print(f"{'Directory':<30} {'Files':<6} {'Dirs':<6} {'Size':<10}")
        print("-" * 40)
        
        for dir_path, stats in sorted(dirs_by_level.items()):
            if dir_path == '.':
                display_name = 'PilotFS/'
            else:
                display_name = f"{dir_path}/"
            
            indent = '  ' * stats['level']
            print(f"{indent}{display_name:<30} {stats['file_count']:<6} {stats['dir_count']:<6} {self._format_size(stats['total_size']):<10}")
    
    def _print_issues_and_recommendations(self):
        """Print issues and recommendations."""
        if not self.issues and not self.warnings:
            print("✅ No major issues found!")
            print("\nRecommended actions:")
            print("1. Restart Enigma2 to load changes")
            print("2. Test player functionality")
            print("3. Check /var/log/messages for any errors")
            return
        
        if self.issues:
            print("🚨 CRITICAL ISSUES (must fix):")
            for issue in self.issues:
                print(f"  • {issue}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS (should fix):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        
        if any("Missing critical file" in issue for issue in self.issues):
            print("1. Restore missing critical files from backup")
        
        if any("compiled files" in issue.lower() for issue in self.issues):
            print("2. Clean compiled files:")
            print("   find . -name \"*.pyc\" -delete")
            print("   find . -name \"*.pyo\" -delete")
            print("   find . -name \"__pycache__\" -exec rm -rf {} +")
        
        if any("player" in warning.lower() for warning in self.warnings):
            print("3. Run player integration update:")
            print("   python3 smart_updater.py .")
        
        print("4. Restart Enigma2 after fixing issues")
        print("5. Run verification again to confirm fixes")
    
    def _generate_report(self):
        """Generate a detailed report file."""
        report_path = self.plugin_path / "structure_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PILOTFS STRUCTURE VERIFICATION REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Plugin path: {self.plugin_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # File listing
            f.write("COMPLETE FILE LISTING:\n")
            f.write("-" * 80 + "\n")
            
            for root, dirs, files in os.walk(self.plugin_path):
                level = root.replace(str(self.plugin_path), '').count(os.sep)
                indent = ' ' * 4 * level
                rel_path = os.path.relpath(root, self.plugin_path)
                
                if rel_path == '.':
                    f.write(f"{indent}PilotFS/\n")
                else:
                    f.write(f"{indent}{os.path.basename(root)}/\n")
                
                subindent = ' ' * 4 * (level + 1)
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    f.write(f"{subindent}{file} ({self._format_size(file_size)})\n")
            
            # Issues summary
            if self.issues or self.warnings:
                f.write("\n" + "=" * 80 + "\n")
                f.write("ISSUES SUMMARY:\n")
                f.write("-" * 80 + "\n")
                
                if self.issues:
                    f.write("\nCRITICAL ISSUES:\n")
                    for issue in self.issues:
                        f.write(f"• {issue}\n")
                
                if self.warnings:
                    f.write("\nWARNINGS:\n")
                    for warning in self.warnings:
                        f.write(f"• {warning}\n")
        
        print(f"\n📝 Detailed report saved to: {report_path}")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python3 verify_structure.py /path/to/pilotfs")
        print("Example: python3 verify_structure.py /usr/lib/enigma2/python/Plugins/Extensions/PilotFS")
        sys.exit(1)
    
    plugin_path = sys.argv[1]
    
    if not os.path.exists(plugin_path):
        print(f"❌ Error: Path does not exist: {plugin_path}")
        sys.exit(1)
    
    verifier = PluginStructureVerifier(plugin_path)
    verifier.verify_complete_structure()


if __name__ == "__main__":
    main()