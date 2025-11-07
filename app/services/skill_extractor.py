from typing import Dict, Set

SIMPLE_NORMALIZATION = {
    # Python
    "python3": "python",
    "py": "python",

    # JavaScript
    "js": "javascript",
    "ecmascript": "javascript",

    # Java
    "java8": "java",
    "java11": "java",

    # C#
    "csharp": "c#",
    "c-sharp": "c#",

    # .NET
    ".net": "dotnet",
    "asp.net": "dotnet",
    "asp.net core": "dotnet",
    "dot net": "dotnet",

    # TypeScript
    "ts": "typescript",

    # Node.js
    "node": "node.js",
    "nodejs": "node.js",

    # Express
    "express": "express.js",

    # React
    "reactjs": "react.js",
    "reactjsx": "react.js",

    # Angular
    "angularjs": "angular",

    # Kubernetes
    "k8s": "kubernetes",
}


class SkillExtractor:
    @staticmethod
    def normalize(skills: Set[str]) -> Dict[str, Set[str]]:
        """
        Normalize skills based on SIMPLE_NORMALIZATION mapping.
        Keeps granularity but collapses trivial variants.
        """
        print("begin skill extractor")
        normalized: Dict[str, Set[str]] = {}

        for skill in skills:
            key = skill.lower().strip()
            canonical = SIMPLE_NORMALIZATION.get(key, key)

            if canonical not in normalized:
                normalized[canonical] = []
            if skill not in normalized[canonical]:
                normalized[canonical].append(skill)

        print("end skill extractor")
        return normalized
