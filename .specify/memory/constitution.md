<!--
SYNC IMPACT REPORT
==================
Version Change: INITIAL → 1.0.0
Change Type: MAJOR (Initial constitution ratification)

Modified Principles:
- Added: I. Clean Code First
- Added: II. Simple UX
- Added: III. Responsive Design
- Added: IV. Minimal Dependencies
- Added: V. No Testing (NON-NEGOTIABLE)

Added Sections:
- Technology Stack
- Development Constraints

Templates Requiring Updates:
✅ plan-template.md - Updated constitution check gates
✅ spec-template.md - Aligned acceptance criteria (removed test requirement)
✅ tasks-template.md - Removed all test-related task phases and examples

Follow-up TODOs: None
-->

# MCP Project SpecKit Constitution

## Core Principles

### I. Clean Code First

Code MUST prioritize readability, maintainability, and simplicity above all else. This means:
- Clear, descriptive variable and function names that communicate intent
- Functions and components kept small and focused on single responsibilities
- Consistent code style and formatting across the entire codebase
- Comments used sparingly—code should be self-documenting wherever possible
- DRY (Don't Repeat Yourself) principle applied rigorously
- Logical file and folder organization that reflects feature boundaries

**Rationale**: Clean code reduces cognitive load, accelerates onboarding, minimizes bugs, and ensures long-term maintainability. In a project without testing, code clarity becomes our primary quality assurance mechanism.

### II. Simple UX

User interfaces MUST be intuitive, straightforward, and require minimal learning. This means:
- Clear visual hierarchy with obvious primary actions
- Minimal clicks/steps to accomplish any user goal
- Consistent interaction patterns throughout the application
- Immediate feedback for all user actions
- Progressive disclosure—show advanced features only when needed
- Error messages that are helpful and actionable
- No unnecessary features or options that clutter the interface

**Rationale**: Simple UX increases user adoption, reduces support burden, and aligns with our minimal dependencies philosophy. Users should be able to accomplish tasks without documentation or training.

### III. Responsive Design

All interfaces MUST work seamlessly across device sizes and orientations. This means:
- Mobile-first design approach with progressive enhancement
- Fluid layouts that adapt naturally to viewport changes
- Touch-friendly interactive elements (minimum 44×44px tap targets)
- Readable typography at all screen sizes
- Optimized images and assets for different resolutions
- Graceful degradation on older browsers while maintaining core functionality
- Performance considerations for mobile networks

**Rationale**: Users expect applications to work on their device of choice. Responsive design is non-negotiable in modern web development and ensures maximum accessibility.

### IV. Minimal Dependencies

External dependencies MUST be minimized and carefully justified. This means:
- Every dependency added requires explicit justification
- Prefer standard library/built-in solutions over third-party packages
- When dependencies are necessary, choose well-maintained, focused libraries over monolithic frameworks
- Regularly audit and remove unused dependencies
- Avoid dependency chains that bring in dozens of sub-dependencies
- Lock dependency versions to prevent unexpected breaking changes
- Document the purpose of each dependency

**Rationale**: Fewer dependencies mean smaller bundle sizes, reduced security vulnerabilities, faster builds, and less maintenance burden from breaking changes in third-party code.

### V. No Testing (NON-NEGOTIABLE)

This project MUST NOT include any form of automated testing. This supersedes all other guidance. Specifically:
- NO unit tests
- NO integration tests
- NO end-to-end tests
- NO test frameworks or testing libraries
- NO test files or test directories
- NO continuous integration testing pipelines

**Rationale**: This is an explicit architectural decision for this project. Quality assurance relies on clean code practices (Principle I), code review, and manual verification. All energy is directed toward production code quality rather than test maintenance.

## Technology Stack

The following technology stack is MANDATORY and versions MUST be respected:

### Frontend
- **React**: ^19.2.0 (UI framework)
- **React DOM**: ^19.2.0 (DOM rendering)
- **Vite**: ^7.2.2 (build tool and dev server)
- **TypeScript**: ~5.9.3 (type safety)
- **Tailwind CSS**: (responsive styling—version per package.json)
- Language: TypeScript/JavaScript (ES modules)
- Node.js version: Compatible with above packages

### Backend
- **Python**: >=3.13 (as specified in pyproject.toml)
- Package management: pip/pyproject.toml
- All packages and versions MUST follow backend/pyproject.toml specifications

### Prohibited Technologies
- Any testing frameworks (Jest, Vitest, Pytest, Mocha, etc.)
- Heavy UI frameworks that conflict with React paradigm
- Deprecated or unmaintained dependencies
- Dependencies that duplicate built-in functionality

## Development Constraints

### Code Quality Gates
Every code change MUST satisfy:
1. **Clean Code Check**: Code review confirms readability and maintainability
2. **UX Simplicity Check**: New features don't complicate existing workflows
3. **Responsive Check**: All UI changes verified on mobile and desktop viewports
4. **Dependency Check**: New dependencies are justified and documented
5. **No Test Code**: Verify no test files or test frameworks were introduced

### Performance Standards
- Frontend bundle size MUST be monitored and justified
- Initial page load MUST be fast even on 3G connections
- Backend API responses SHOULD complete in <200ms for typical operations
- Images and assets MUST be optimized for web delivery

### Documentation Requirements
- README files MUST exist for frontend and backend directories
- Complex algorithms or business logic MUST have inline explanatory comments
- Architecture decisions MUST be documented (e.g., in ADR format if appropriate)
- Dependency additions MUST be documented with rationale

## Governance

This constitution supersedes all other practices, guidelines, and conventions. All development work MUST comply with these principles.

### Amendment Process
- Amendments require explicit documentation of the change and rationale
- Version number MUST be incremented using semantic versioning:
  - **MAJOR**: Backward incompatible changes (e.g., removing a principle)
  - **MINOR**: New principles or significant expansions
  - **PATCH**: Clarifications, wording improvements, non-semantic refinements
- Last Amended date MUST be updated to change date

### Compliance
- All code reviews MUST verify constitutional compliance
- Principle violations MUST be caught and corrected in review
- When principles conflict, resolve via explicit discussion and document the decision
- This constitution is the single source of truth for project standards

### Versioning Policy
This document follows semantic versioning. Changes to principles require version increments as specified above.

**Version**: 1.0.0 | **Ratified**: 2025-11-10 | **Last Amended**: 2025-11-10
