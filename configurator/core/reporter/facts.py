import random
from typing import Dict, List, Optional


class FactsDatabase:
    """Database of tips and facts for display during installation."""

    FACTS: Dict[str, List[str]] = {
        "docker": [
            "Docker uses containerization to isolate applications without VM overhead.",
            "A Docker container shares the host kernel, making it lighter than VMs.",
            "Docker Hub contains over 6 million container images.",
            "Docker Compose can orchestrate multi-container applications.",
        ],
        "python": [
            "Python is named after Monty Python, not the snake! ",
            "Python uses indentation to define code blocks instead of braces.",
            "The Zen of Python: 'Simple is better than complex.'",
            "Python 3.12 introduced a 5% performance improvement over 3.11.",
        ],
        "security": [
            "Fail2ban monitors logs and blocks suspicious IP addresses.",
            "UFW (Uncomplicated Firewall) is a user-friendly firewall interface.",
            "SSH key authentication is more secure than passwords.",
            "Regular security updates are crucial for server safety.",
        ],
        "linux": [
            "Linux powers over 90% of public cloud workloads.",
            "The Linux kernel has over 27 million lines of code.",
            "Debian is one of the oldest Linux distributions (since 1993).",
            "Everything in Linux is a file, including hardware devices.",
        ],
        "general": [
            "Taking breaks during long installations is recommended! ",
            "You can monitor progress in real-time with the TUI dashboard.",
            "Installation logs are saved for troubleshooting.",
            "Dry-run mode lets you preview changes without applying them.",
        ],
    }

    @classmethod
    def get_random_fact(cls, category: Optional[str] = None) -> str:
        """
        Get random fact from category.

        Args:
            category:  Fact category (docker, python, etc.)

        Returns:
            Random fact string
        """
        if category and category in cls.FACTS:
            facts = cls.FACTS[category]
        else:
            # Random category
            all_facts = []
            for facts_list in cls.FACTS.values():
                all_facts.extend(facts_list)
            facts = all_facts

        return random.choice(facts)

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get list of all fact categories."""
        return list(cls.FACTS.keys())
