#!/usr/bin/env python3
"""
Minimal version of vibe status logic for focused mutation testing.
"""

import subprocess
from pathlib import Path
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result  # for the yield case
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result  # for the yield case
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_yield_from_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = yield from orig(*call_args, **call_kwargs)
        return result  # for the yield case
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = yield from orig(*call_args, **call_kwargs)
        return result  # for the yield case
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = yield from mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = yield from mutants[mutant_name](*call_args, **call_kwargs)
    return result


class VibeSession:
    """Represents the current vibe session state"""

    def xǁVibeSessionǁ__init____mutmut_orig(self):
        self.branch_name = None
        self.is_vibing = False
        self.observer = None
        self.commit_event = None

    def xǁVibeSessionǁ__init____mutmut_1(self):
        self.branch_name = ""
        self.is_vibing = False
        self.observer = None
        self.commit_event = None

    def xǁVibeSessionǁ__init____mutmut_2(self):
        self.branch_name = None
        self.is_vibing = None
        self.observer = None
        self.commit_event = None

    def xǁVibeSessionǁ__init____mutmut_3(self):
        self.branch_name = None
        self.is_vibing = True
        self.observer = None
        self.commit_event = None

    def xǁVibeSessionǁ__init____mutmut_4(self):
        self.branch_name = None
        self.is_vibing = False
        self.observer = ""
        self.commit_event = None

    def xǁVibeSessionǁ__init____mutmut_5(self):
        self.branch_name = None
        self.is_vibing = False
        self.observer = None
        self.commit_event = ""
    
    xǁVibeSessionǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁVibeSessionǁ__init____mutmut_1': xǁVibeSessionǁ__init____mutmut_1, 
        'xǁVibeSessionǁ__init____mutmut_2': xǁVibeSessionǁ__init____mutmut_2, 
        'xǁVibeSessionǁ__init____mutmut_3': xǁVibeSessionǁ__init____mutmut_3, 
        'xǁVibeSessionǁ__init____mutmut_4': xǁVibeSessionǁ__init____mutmut_4, 
        'xǁVibeSessionǁ__init____mutmut_5': xǁVibeSessionǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁVibeSessionǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁVibeSessionǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁVibeSessionǁ__init____mutmut_orig)
    xǁVibeSessionǁ__init____mutmut_orig.__name__ = 'xǁVibeSessionǁ__init__'


def x_find_git_repo__mutmut_orig() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_1() -> Path:
    """Find the git repository root"""
    current = None
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_2() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current == current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_3() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current * ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_4() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / "XX.gitXX").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_5() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".GIT").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_6() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = None
    raise RuntimeError("Not in a git repository")


def x_find_git_repo__mutmut_7() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError(None)


def x_find_git_repo__mutmut_8() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("XXNot in a git repositoryXX")


def x_find_git_repo__mutmut_9() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("not in a git repository")


def x_find_git_repo__mutmut_10() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("NOT IN A GIT REPOSITORY")

x_find_git_repo__mutmut_mutants : ClassVar[MutantDict] = {
'x_find_git_repo__mutmut_1': x_find_git_repo__mutmut_1, 
    'x_find_git_repo__mutmut_2': x_find_git_repo__mutmut_2, 
    'x_find_git_repo__mutmut_3': x_find_git_repo__mutmut_3, 
    'x_find_git_repo__mutmut_4': x_find_git_repo__mutmut_4, 
    'x_find_git_repo__mutmut_5': x_find_git_repo__mutmut_5, 
    'x_find_git_repo__mutmut_6': x_find_git_repo__mutmut_6, 
    'x_find_git_repo__mutmut_7': x_find_git_repo__mutmut_7, 
    'x_find_git_repo__mutmut_8': x_find_git_repo__mutmut_8, 
    'x_find_git_repo__mutmut_9': x_find_git_repo__mutmut_9, 
    'x_find_git_repo__mutmut_10': x_find_git_repo__mutmut_10
}

def find_git_repo(*args, **kwargs):
    result = _mutmut_trampoline(x_find_git_repo__mutmut_orig, x_find_git_repo__mutmut_mutants, args, kwargs)
    return result 

find_git_repo.__signature__ = _mutmut_signature(x_find_git_repo__mutmut_orig)
x_find_git_repo__mutmut_orig.__name__ = 'x_find_git_repo'


def x_run_git_command__mutmut_orig(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_1(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = None
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_2(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            None,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_3(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=None,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_4(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=None,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_5(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=None,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_6(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=None,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_7(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_8(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_9(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_10(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_11(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_12(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["XXgitXX"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_13(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["GIT"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_14(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["Git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_15(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] - args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_16(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd and find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_17(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=False,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_18(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=False,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_19(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_20(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode != 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_21(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 1, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_22(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() and result.stderr.strip()
    except Exception as e:
        return False, str(e)


def x_run_git_command__mutmut_23(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return True, str(e)


def x_run_git_command__mutmut_24(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(None)

x_run_git_command__mutmut_mutants : ClassVar[MutantDict] = {
'x_run_git_command__mutmut_1': x_run_git_command__mutmut_1, 
    'x_run_git_command__mutmut_2': x_run_git_command__mutmut_2, 
    'x_run_git_command__mutmut_3': x_run_git_command__mutmut_3, 
    'x_run_git_command__mutmut_4': x_run_git_command__mutmut_4, 
    'x_run_git_command__mutmut_5': x_run_git_command__mutmut_5, 
    'x_run_git_command__mutmut_6': x_run_git_command__mutmut_6, 
    'x_run_git_command__mutmut_7': x_run_git_command__mutmut_7, 
    'x_run_git_command__mutmut_8': x_run_git_command__mutmut_8, 
    'x_run_git_command__mutmut_9': x_run_git_command__mutmut_9, 
    'x_run_git_command__mutmut_10': x_run_git_command__mutmut_10, 
    'x_run_git_command__mutmut_11': x_run_git_command__mutmut_11, 
    'x_run_git_command__mutmut_12': x_run_git_command__mutmut_12, 
    'x_run_git_command__mutmut_13': x_run_git_command__mutmut_13, 
    'x_run_git_command__mutmut_14': x_run_git_command__mutmut_14, 
    'x_run_git_command__mutmut_15': x_run_git_command__mutmut_15, 
    'x_run_git_command__mutmut_16': x_run_git_command__mutmut_16, 
    'x_run_git_command__mutmut_17': x_run_git_command__mutmut_17, 
    'x_run_git_command__mutmut_18': x_run_git_command__mutmut_18, 
    'x_run_git_command__mutmut_19': x_run_git_command__mutmut_19, 
    'x_run_git_command__mutmut_20': x_run_git_command__mutmut_20, 
    'x_run_git_command__mutmut_21': x_run_git_command__mutmut_21, 
    'x_run_git_command__mutmut_22': x_run_git_command__mutmut_22, 
    'x_run_git_command__mutmut_23': x_run_git_command__mutmut_23, 
    'x_run_git_command__mutmut_24': x_run_git_command__mutmut_24
}

def run_git_command(*args, **kwargs):
    result = _mutmut_trampoline(x_run_git_command__mutmut_orig, x_run_git_command__mutmut_mutants, args, kwargs)
    return result 

run_git_command.__signature__ = _mutmut_signature(x_run_git_command__mutmut_orig)
x_run_git_command__mutmut_orig.__name__ = 'x_run_git_command'


def x_vibe_status__mutmut_orig(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_1(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = None

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_2(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = None
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_3(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            None, repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_4(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], None
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_5(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_6(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_7(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["XXbranchXX", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_8(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["BRANCH", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_9(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["Branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_10(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "XX--show-currentXX"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_11(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--SHOW-CURRENT"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_12(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_13(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "XX⚪ NOT INITIALIZED: Could not determine current branchXX"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_14(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ not initialized: could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_15(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: COULD NOT DETERMINE CURRENT BRANCH"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_16(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ not initialized: could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_17(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = None  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_18(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing or session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_19(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch != session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_20(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = None
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_21(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = True
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_22(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = ""

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_23(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith(None) and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_24(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("XXvibe-XX") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_25(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("VIBE-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_26(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("Vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_27(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") or not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_28(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_29(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "XX🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!XX"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_30(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 idle: ready to start vibing. call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_31(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: READY TO START VIBING. CALL START_VIBING() TO BEGIN!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


def x_vibe_status__mutmut_32(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 idle: ready to start vibing. call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"

x_vibe_status__mutmut_mutants : ClassVar[MutantDict] = {
'x_vibe_status__mutmut_1': x_vibe_status__mutmut_1, 
    'x_vibe_status__mutmut_2': x_vibe_status__mutmut_2, 
    'x_vibe_status__mutmut_3': x_vibe_status__mutmut_3, 
    'x_vibe_status__mutmut_4': x_vibe_status__mutmut_4, 
    'x_vibe_status__mutmut_5': x_vibe_status__mutmut_5, 
    'x_vibe_status__mutmut_6': x_vibe_status__mutmut_6, 
    'x_vibe_status__mutmut_7': x_vibe_status__mutmut_7, 
    'x_vibe_status__mutmut_8': x_vibe_status__mutmut_8, 
    'x_vibe_status__mutmut_9': x_vibe_status__mutmut_9, 
    'x_vibe_status__mutmut_10': x_vibe_status__mutmut_10, 
    'x_vibe_status__mutmut_11': x_vibe_status__mutmut_11, 
    'x_vibe_status__mutmut_12': x_vibe_status__mutmut_12, 
    'x_vibe_status__mutmut_13': x_vibe_status__mutmut_13, 
    'x_vibe_status__mutmut_14': x_vibe_status__mutmut_14, 
    'x_vibe_status__mutmut_15': x_vibe_status__mutmut_15, 
    'x_vibe_status__mutmut_16': x_vibe_status__mutmut_16, 
    'x_vibe_status__mutmut_17': x_vibe_status__mutmut_17, 
    'x_vibe_status__mutmut_18': x_vibe_status__mutmut_18, 
    'x_vibe_status__mutmut_19': x_vibe_status__mutmut_19, 
    'x_vibe_status__mutmut_20': x_vibe_status__mutmut_20, 
    'x_vibe_status__mutmut_21': x_vibe_status__mutmut_21, 
    'x_vibe_status__mutmut_22': x_vibe_status__mutmut_22, 
    'x_vibe_status__mutmut_23': x_vibe_status__mutmut_23, 
    'x_vibe_status__mutmut_24': x_vibe_status__mutmut_24, 
    'x_vibe_status__mutmut_25': x_vibe_status__mutmut_25, 
    'x_vibe_status__mutmut_26': x_vibe_status__mutmut_26, 
    'x_vibe_status__mutmut_27': x_vibe_status__mutmut_27, 
    'x_vibe_status__mutmut_28': x_vibe_status__mutmut_28, 
    'x_vibe_status__mutmut_29': x_vibe_status__mutmut_29, 
    'x_vibe_status__mutmut_30': x_vibe_status__mutmut_30, 
    'x_vibe_status__mutmut_31': x_vibe_status__mutmut_31, 
    'x_vibe_status__mutmut_32': x_vibe_status__mutmut_32
}

def vibe_status(*args, **kwargs):
    result = _mutmut_trampoline(x_vibe_status__mutmut_orig, x_vibe_status__mutmut_mutants, args, kwargs)
    return result 

vibe_status.__signature__ = _mutmut_signature(x_vibe_status__mutmut_orig)
x_vibe_status__mutmut_orig.__name__ = 'x_vibe_status'