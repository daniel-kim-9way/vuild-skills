# Vuild LEARN 스킬 — 마켓플레이스로 한 번에 설치

이 레포는 **Claude Code 플러그인 마켓플레이스**입니다.
명령 두 줄이면 LEARN 커리큘럼 스킬 28개가 한꺼번에 설치됩니다.

> ⚠️ 설치 명령(`/plugin ...`)은 **Claude Code(터미널 CLI 또는 VS Code/JetBrains 확장)** 에서 실행합니다.
> Claude Desktop 앱 단독 화면에는 커스텀 마켓플레이스를 추가하는 메뉴가 없습니다.
> 단, Claude Code에서 한 번 설치하면 그 스킬은 Claude Desktop chat·Cowork에서도 함께 사용됩니다.

## 설치 (Claude Code에서)

```
/plugin marketplace add daniel-kim-9way/learn-skills
/plugin install vuild-learn-skills@vuild-learn
/reload-plugins
```

- 첫 줄: 이 GitHub 레포를 마켓플레이스로 등록
- 둘째 줄: `vuild-learn-skills` 플러그인(스킬 28개) 설치
- 셋째 줄: 재시작 없이 즉시 활성화

설치 후 스킬은 플러그인 이름이 붙어 호출됩니다:

```
/vuild-learn-skills:v1-discover
/vuild-learn-skills:v3-auth
...
```

## 업데이트

레포에 변경을 push한 뒤, 사용자는 아래 한 줄로 최신화합니다.

```
/plugin marketplace update vuild-learn
```

> 새 버전을 받게 하려면 [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) 의
> `version` 값을 올리세요. (예: `2.0.0` → `2.0.1`)

## 제거

```
/plugin uninstall vuild-learn-skills@vuild-learn
```

## 구조

```
.claude-plugin/marketplace.json          ← 마켓플레이스 카탈로그
plugins/vuild-learn-skills/
  ├── .claude-plugin/plugin.json         ← 플러그인 메타데이터
  └── skills/                            ← 스킬 28개 (배포본)
      ├── v1-discover/SKILL.md
      └── ...
```

> 레포 루트의 `v1-*` 등 스킬 폴더는 **Claude Desktop UI 업로드용 원본**이고,
> `plugins/vuild-learn-skills/skills/` 는 **마켓플레이스 배포본**입니다.
> 콘텐츠 수정 시 두 곳을 함께 맞춰 주세요. (정본: vuild 레포의 `db/seeds/ch*_lessons.rb` → `skills/`)
