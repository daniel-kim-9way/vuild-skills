// 동화 공방 확인 화면. 데이터는 <script id="data">에 있고, 고친 내용을 글로 모아 복사한다.
// 사람이 쓴 글은 늘 textContent로 넣는다(innerHTML을 쓰지 않는다).
(function () {
  "use strict"
  const data = JSON.parse(document.getElementById("data").textContent)
  const app = document.getElementById("app")
  const collectors = []
  document.title = `${data.screen} · ${data.title || "동화 공방"}`

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag)
    for (const [key, value] of Object.entries(attrs || {})) {
      if (value === null || value === undefined || value === false) continue
      if (key === "class") node.className = value
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value)
      else node.setAttribute(key, value === true ? "" : value)
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue
      node.append(child instanceof Node ? child : document.createTextNode(String(child)))
    }
    return node
  }

  const src = (path) => (path ? encodeURI(path) : null)
  const said = (input) => input.value.trim()

  function header(lead) {
    return el("header", {},
      el("p", { class: "eyebrow" }, `동화 공방 · ${data.screen}`),
      el("h1", {}, data.title || "동화 공방"),
      lead ? el("p", { class: "lead" }, lead) : null)
  }

  function castRow() {
    return el("section", { class: "cast" }, data.cast.map((c) =>
      el("figure", {}, el("img", { src: src(c.photo), alt: c.name }),
        el("figcaption", {}, c.kind && c.kind !== "아이" ? `${c.name} (${c.kind})` : c.name))))
  }

  function questions() {
    if (!data.questions || !data.questions.length) return null
    return el("section", { class: "questions" }, el("h2", {}, "다 읽고 물어보세요"),
      el("ul", {}, data.questions.map((q) => el("li", {}, q))))
  }

  function noteBox() {
    const note = el("textarea", { rows: 2, placeholder: "더 하고 싶은 말이 있으면 적어 주세요" })
    app.append(el("section", { class: "more" }, el("h2", {}, "더 하고 싶은 말"), note))
    collectors.push(() => (said(note) ? [`더 하고 싶은 말: ${said(note)}`] : []))
  }

  function draftScreen() {
    app.append(header("글을 바로 고치거나, 다시 써 달라고 표시하세요. 다 되면 아래 버튼을 눌러요."), castRow())
    const list = el("section", { class: "pages" })
    for (const page of data.pages) {
      const box = el("textarea", { rows: page.n === 0 ? 1 : 3, "aria-label": `${page.label} 글` })
      box.value = page.text
      const again = el("input", { type: "checkbox" })
      const why = el("input", { type: "text", placeholder: "어떻게 바꾸면 좋을까요? (안 적어도 돼요)" })
      list.append(el("article", { class: "page" }, el("h3", {}, page.label), box,
        el("label", { class: "check" }, again, page.n === 0 ? " 제목을 다시 지어 줘" : " 이 쪽을 다시 써 줘"), why))
      collectors.push(() => {
        const lines = []
        if (said(box) && said(box) !== page.text) lines.push(`${page.label} 고친 글: "${said(box)}"`)
        if (again.checked) lines.push(`${page.label} 다시 써 줘${said(why) ? `: ${said(why)}` : ""}`)
        else if (said(why)) lines.push(`${page.label}: ${said(why)}`)
        return lines
      })
    }
    app.append(list, questions())
    const whole = el("input", { type: "checkbox" })
    app.append(el("label", { class: "check" }, whole, " 이야기를 통째로 다시 써 줘"))
    collectors.push(() => (whole.checked ? ["이야기를 통째로 다시 써 줘"] : []))
    noteBox()
    return "좋아요. 이대로 그림을 그려 주세요."
  }

  function artScreen() {
    app.append(header("그림을 보고, 다시 그릴 쪽에 표시하세요. 다 되면 아래 버튼을 눌러요."))
    const grid = el("section", { class: "grid" })
    for (const page of data.pages) {
      const again = el("input", { type: "checkbox" })
      const why = el("input", { type: "text", placeholder: "왜 다시 그릴까요? (예: 손가락이 세 개여야 해요)" })
      grid.append(el("article", { class: "card" },
        page.image ? el("img", { src: src(page.image), alt: page.label }) : el("div", { class: "empty" }, "아직 안 그렸어요"),
        el("h3", {}, page.label), el("p", {}, page.text),
        page.note ? el("p", { class: "note" }, `다시 그린 까닭: ${page.note}`) : null,
        el("label", { class: "check" }, again, " 다시 그리기"), why))
      collectors.push(() => (again.checked || said(why) ? [`${page.label} 다시 그리기${said(why) ? `: ${said(why)}` : ""}`] : []))
    }
    app.append(grid)
    noteBox()
    return "그림 좋아요. 목소리와 MP4를 만들어 주세요."
  }

  function bookScreen() {
    app.append(header(data.lesson))
    if (data.video) app.append(el("video", { src: src(data.video), controls: true, preload: "metadata" }))
    let index = 0
    const picture = el("img", { alt: "" })
    const caption = el("p", { class: "caption" })
    const count = el("span", {})
    const show = (i) => {
      index = (i + data.pages.length) % data.pages.length
      const page = data.pages[index]
      picture.src = src(page.image) || ""
      picture.alt = page.label
      caption.textContent = page.text
      count.textContent = `${index + 1} / ${data.pages.length}`
    }
    app.append(el("section", { class: "flip" }, picture, caption,
      el("div", { class: "nav" },
        el("button", { type: "button", onclick: () => show(index - 1) }, "◀ 앞으로"), count,
        el("button", { type: "button", onclick: () => show(index + 1) }, "다음 ▶"))))
    show(0)
    app.append(questions())
    app.append(el("h2", {}, "고칠 곳이 있으면"))
    const which = el("select", { "aria-label": "쪽" }, data.pages.map((p) => el("option", { value: p.label }, p.label)))
    const what = el("select", { "aria-label": "고칠 것" },
      el("option", { value: "그림 다시 그리기" }, "그림 다시 그리기"), el("option", { value: "글 고치기" }, "글 고치기"))
    const why = el("input", { type: "text", placeholder: "어떻게 고칠까요?" })
    const added = el("ul", { class: "requests" })
    const requests = []
    app.append(el("div", { class: "request" }, which, what, why, el("button", {
      type: "button",
      onclick: () => {
        if (!said(why) && what.value === "글 고치기") { why.focus(); return }
        const line = `${which.value} ${what.value}${said(why) ? `: ${said(why)}` : ""}`
        requests.push(line)
        added.append(el("li", {}, line))
        why.value = ""
      },
    }, "더하기")), added)
    collectors.push(() => requests.slice())
    noteBox()
    return null
  }

  function voiceScreen() {
    app.append(header("세 목소리를 들어 보고 하나를 고르세요."))
    const group = el("section", { class: "voices" })
    data.voices.forEach((v, i) => {
      group.append(el("label", { class: "voice" },
        el("input", { type: "radio", name: "voice", value: v.id, checked: i === 0 }), ` ${v.label}`,
        el("audio", { src: src(v.file), controls: true, preload: "none" })))
    })
    app.append(group)
    collectors.push(() => {
      const picked = document.querySelector("input[name=voice]:checked")
      const chosen = data.voices.find((v) => v.id === picked.value)
      return [`${chosen.label} 목소리(${chosen.id})로 할게요`]
    })
    return null
  }

  const screens = { draft: draftScreen, art: artScreen, book: bookScreen, voice: voiceScreen }
  const whenNothing = screens[data.kind]()

  function message() {
    const head = data.folder ? `[동화 공방 · ${data.screen}] ${data.folder}` : `[동화 공방 · ${data.screen}]`
    const lines = collectors.flatMap((collect) => collect())
    if (!lines.length && !whenNothing) return null
    return [head, ...(lines.length ? lines : [whenNothing])].join("\n")
  }
  window.storybookMessage = message // 브라우저 검사에서 쓴다

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch (e) { /* 파일로 연 화면에서 막히면 아래 방법으로 */ }
    const area = el("textarea", { readonly: true, style: "position:fixed;top:0;left:0;opacity:0" })
    area.value = text
    document.body.append(area)
    area.select()
    let ok = false
    try { ok = document.execCommand("copy") } catch (e) { ok = false }
    area.remove()
    return ok
  }

  const status = document.getElementById("copied")
  const fallback = document.getElementById("fallback")
  document.getElementById("copy").addEventListener("click", async () => {
    const text = message()
    status.hidden = false
    if (!text) {
      status.textContent = "고칠 곳을 먼저 적어 주세요."
      return
    }
    if (await copy(text)) {
      fallback.hidden = true
      status.textContent = "복사했어요. 터미널에 붙여 넣으세요 (Ctrl+V, Mac은 ⌘V)"
    } else {
      fallback.value = text
      fallback.hidden = false
      fallback.focus()
      fallback.select()
      status.textContent = "자동 복사가 막혔어요. 아래 글이 선택돼 있으니 Ctrl+C(Mac은 ⌘C)를 누르세요."
    }
  })
})()
