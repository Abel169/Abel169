// =====================================================================
//  SOGOBA CREATIVE - Script de test After Effects 2024 (Windows)
//  Cree une composition 1080x1920, 10 s, 30 i/s, sans plugin.
//  Utilisation : Fichier > Scripts > Executer le fichier de script...
//  Tout est construit avec les "matchNames" internes : marche aussi
//  avec After Effects en francais.
// =====================================================================
(function () {
    var W = 1080, H = 1920, DUR = 10, FPS = 30;
    var FONT_BIG = "Arial-Black";      // police presente sur Windows
    var FONT_TXT = "Arial-BoldMT";

    function rgb(hex) {
        return [parseInt(hex.substr(1, 2), 16) / 255, parseInt(hex.substr(3, 2), 16) / 255, parseInt(hex.substr(5, 2), 16) / 255];
    }
    var C_BG1 = rgb("#07070C"), C_BG2 = rgb("#2A1450"), C_CYAN = rgb("#25F4EE"),
        C_VIOLET = rgb("#8B5CF6"), C_PINK = rgb("#FE2C55"), C_WHITE = [1, 1, 1];

    // ---------- helpers ----------
    function tr(layer, mn) { return layer.property("ADBE Transform Group").property(mn); }

    function easeDims(prop) {
        var t = prop.propertyValueType;
        if (t === PropertyValueType.TwoD_SPATIAL || t === PropertyValueType.ThreeD_SPATIAL) return 1;
        if (t === PropertyValueType.TwoD) return 2;
        if (t === PropertyValueType.ThreeD) return 3;
        return 1;
    }
    // keys = [[time, value], ...] ; ease "out" = fin douce, "in" = depart doux, "both"
    function anim(prop, keys, easeIn, easeOut) {
        var i, k, n = easeDims(prop);
        for (i = 0; i < keys.length; i++) prop.setValueAtTime(keys[i][0], keys[i][1]);
        for (i = 1; i <= prop.numKeys; i++) {
            var inA = [], outA = [];
            for (k = 0; k < n; k++) {
                inA.push(new KeyframeEase(0, easeIn || 80));
                outA.push(new KeyframeEase(0, easeOut || 80));
            }
            try { prop.setTemporalEaseAtKey(i, inA, outA); } catch (e) {}
        }
    }

    function addText(comp, name, str, font, size, color, tracking) {
        var l = comp.layers.addText(str);
        l.name = name;
        var tp = l.property("ADBE Text Properties").property("ADBE Text Document");
        var td = tp.value;
        try { td.resetCharStyle(); } catch (e) {}
        td.text = str;
        td.font = font;
        td.fontSize = size;
        td.applyFill = true;
        td.fillColor = color;
        td.applyStroke = false;
        td.tracking = tracking || 0;
        td.justification = ParagraphJustification.CENTER_JUSTIFY;
        tp.setValue(td);
        // ancre au centre du texte
        var r = l.sourceRectAtTime(0, false);
        tr(l, "ADBE Anchor Point").setValue([r.left + r.width / 2, r.top + r.height / 2]);
        return l;
    }

    // animateur "lettres qui montent" (position + opacite + flou), en francais ou anglais
    function addRiseAnimator(layer, t0, t1, dy) {
        var anims = layer.property("ADBE Text Properties").property("ADBE Text Animators");
        var a = anims.addProperty("ADBE Text Animator");
        a.name = "Montee";
        var idx = a.propertyIndex;
        layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx)
            .property("ADBE Text Animator Properties").addProperty("ADBE Text Position 3D");
        layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx)
            .property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity");
        try {
            layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx)
                .property("ADBE Text Animator Properties").addProperty("ADBE Text Blur");
        } catch (e) {}
        a = layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx);
        var ap = a.property("ADBE Text Animator Properties");
        ap.property("ADBE Text Position 3D").setValue([0, dy, 0]);
        ap.property("ADBE Text Opacity").setValue(0);
        try { ap.property("ADBE Text Blur").setValue([0, 40]); } catch (e) {}
        var sel = a.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
        a = layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx);
        sel = a.property("ADBE Text Selectors").property(1);
        try { sel.property("ADBE Text Range Advanced").property("ADBE Text Range Shape").setValue(2); } catch (e) {} // rampe montante
        anim(sel.property("ADBE Text Percent Start"), [[t0, 0], [t1, 100]], 60, 90);
    }

    function addTrackingAnimator(layer, keys) {
        var anims = layer.property("ADBE Text Properties").property("ADBE Text Animators");
        var a = anims.addProperty("ADBE Text Animator");
        a.name = "Espacement";
        var idx = a.propertyIndex;
        layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx)
            .property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
        a = layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx);
        a.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
        a = layer.property("ADBE Text Properties").property("ADBE Text Animators").property(idx);
        anim(a.property("ADBE Text Animator Properties").property("ADBE Text Tracking Amount"), keys, 70, 90);
    }

    function addShape(comp, name) {
        var l = comp.layers.addShape();
        l.name = name;
        return l;
    }
    function shapeGroup(layer) {
        var g = layer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        return layer.property("ADBE Root Vectors Group").property(g.propertyIndex);
    }

    // ---------- projet ----------
    app.beginUndoGroup("Sogoba - test");
    if (!app.project) app.newProject();
    var folder = app.project.items.addFolder("SOGOBA_TEST");
    var comp = app.project.items.addComp("SOGOBA_TEST_9x16", W, H, 1, DUR, FPS);
    comp.parentFolder = folder;
    comp.motionBlur = true;
    comp.bgColor = C_BG1;

    // ---------- 1. fond degrade (Degrade de couleurs / Gradient Ramp) ----------
    var bg = comp.layers.addSolid(C_BG1, "Fond", W, H, 1, DUR);
    var ramp = bg.property("ADBE Effect Parade").addProperty("ADBE Ramp");
    ramp.property(1).setValue([W / 2, H * 0.35]);   // debut
    ramp.property(2).setValue(C_BG2);              // couleur debut
    ramp.property(3).setValue([W / 2, H * 1.05]);  // fin
    ramp.property(4).setValue(C_BG1);              // couleur fin
    ramp.property(5).setValue(2);                  // radial
    // le centre du degrade respire doucement (expression)
    ramp.property(1).expression = "[" + (W / 2) + " + Math.sin(time*0.8)*120, " + (H * 0.35) + " + Math.cos(time*0.6)*80]";

    // ---------- 2. cercle lumineux ----------
    var orb = addShape(comp, "Cercle");
    var g1 = shapeGroup(orb);
    g1.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse");
    g1 = orb.property("ADBE Root Vectors Group").property(1);
    g1.property("ADBE Vectors Group").property(1).property("ADBE Vector Ellipse Size").setValue([620, 620]);
    g1.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
    g1 = orb.property("ADBE Root Vectors Group").property(1);
    g1.property("ADBE Vectors Group").property(2).property("ADBE Vector Fill Color").setValue(C_VIOLET);
    tr(orb, "ADBE Position").setValue([W / 2, 820]);
    anim(tr(orb, "ADBE Scale"), [[0, [0, 0, 100]], [0.7, [112, 112, 100]], [1.0, [100, 100, 100]], [5.2, [100, 100, 100]], [6.0, [420, 420, 100]]], 60, 85);
    anim(tr(orb, "ADBE Opacity"), [[0, 75], [5.6, 75], [6.2, 0]], 60, 80);
    tr(orb, "ADBE Position").expression = "wiggle(0.6, 25)";
    var blurOrb = orb.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2");
    blurOrb.property(1).setValue(120);
    orb.blendingMode = BlendingMode.SCREEN;

    // ---------- 3. cadre qui se dessine (Trim Paths / Raccorder les traces) ----------
    var frame = addShape(comp, "Cadre");
    var g2 = shapeGroup(frame);
    g2.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
    g2 = frame.property("ADBE Root Vectors Group").property(1);
    g2.property("ADBE Vectors Group").property(1).property("ADBE Vector Rect Size").setValue([880, 1100]);
    g2.property("ADBE Vectors Group").property(1).property("ADBE Vector Rect Roundness").setValue(60);
    g2.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Stroke");
    g2 = frame.property("ADBE Root Vectors Group").property(1);
    g2.property("ADBE Vectors Group").property(2).property("ADBE Vector Stroke Color").setValue(C_CYAN);
    g2.property("ADBE Vectors Group").property(2).property("ADBE Vector Stroke Width").setValue(6);
    g2.property("ADBE Vectors Group").addProperty("ADBE Vector Filter - Trim");
    g2 = frame.property("ADBE Root Vectors Group").property(1);
    var trim = g2.property("ADBE Vectors Group").property(3);
    anim(trim.property("ADBE Vector Trim End"), [[0.3, 0], [1.6, 100]], 50, 90);
    anim(trim.property("ADBE Vector Trim Start"), [[7.8, 0], [8.6, 100]], 70, 70);
    trim.property("ADBE Vector Trim Offset").expression = "time*20";
    tr(frame, "ADBE Position").setValue([W / 2, 900]);
    var glowF = frame.property("ADBE Effect Parade").addProperty("ADBE Glo2");
    try { glowF.property("ADBE Glo2-0003").setValue(40); glowF.property("ADBE Glo2-0004").setValue(1.5); } catch (e) {}

    // ---------- 4. textes en 3D ----------
    var t1 = addText(comp, "SOGOBA", "SOGOBA", FONT_BIG, 190, C_WHITE, -20);
    t1.threeDLayer = true;
    tr(t1, "ADBE Position").setValue([W / 2, 820, 0]);
    addRiseAnimator(t1, 0.6, 1.8, 220);
    var glowT = t1.property("ADBE Effect Parade").addProperty("ADBE Glo2");
    try { glowT.property("ADBE Glo2-0003").setValue(25); glowT.property("ADBE Glo2-0004").setValue(0.6); } catch (e) {}

    var t2 = addText(comp, "CREATIVE", "CR\u00C9ATIVE", FONT_TXT, 96, C_CYAN, 0);
    t2.threeDLayer = true;
    tr(t2, "ADBE Position").setValue([W / 2, 1000, -150]);
    addTrackingAnimator(t2, [[1.2, 400], [2.4, 0], [7.6, 0], [8.4, 600]]);
    anim(tr(t2, "ADBE Opacity"), [[1.2, 0], [1.7, 100], [7.9, 100], [8.4, 0]], 60, 80);

    var t3 = addText(comp, "Badge", "TEST AFTER EFFECTS 2024", FONT_TXT, 44, C_WHITE, 120);
    t3.threeDLayer = true;
    tr(t3, "ADBE Position").setValue([W / 2, 1220, -300]);
    addRiseAnimator(t3, 2.6, 3.6, 80);

    // sortie de SOGOBA : il recule dans la profondeur
    anim(tr(t1, "ADBE Position"), [[7.6, [W / 2, 820, 0]], [8.6, [W / 2, 820, 1800]]], 80, 60);
    anim(tr(t1, "ADBE Opacity"), [[8.0, 100], [8.6, 0]], 60, 60);
    anim(tr(t3, "ADBE Opacity"), [[7.6, 100], [8.2, 0]], 60, 60);

    // ---------- 5. fin : coche ----------
    var ok = addText(comp, "OK", "SCRIPT OK !", FONT_BIG, 110, C_WHITE, 0);
    tr(ok, "ADBE Position").setValue([W / 2, 900]);
    ok.inPoint = 8.4;
    anim(tr(ok, "ADBE Scale"), [[8.4, [0, 0, 100]], [8.9, [115, 115, 100]], [9.2, [100, 100, 100]]], 70, 85);
    var fillOk = ok.property("ADBE Effect Parade").addProperty("ADBE Fill");
    try { fillOk.property("ADBE Fill-0002").setValue(C_PINK); } catch (e) {}
    if (fillOk.property("ADBE Fill-0002")) fillOk.property("ADBE Fill-0002").expression = "t=time*1.2; [ (Math.sin(t)+1)/2*0.15+0.85, (Math.sin(t+2)+1)/2*0.3+0.17, (Math.sin(t+4)+1)/2*0.6+0.33, 1]";

    // ---------- 6. camera 3D qui avance lentement ----------
    var cam = comp.layers.addCamera("Camera", [W / 2, H / 2]);
    var cpos = tr(cam, "ADBE Position").value;
    anim(tr(cam, "ADBE Position"), [[0, [cpos[0], cpos[1], cpos[2] - 300]], [DUR, [cpos[0], cpos[1], cpos[2] + 150]]], 40, 40);
    try {
        var co = cam.property("ADBE Camera Options Group");
        co.property("ADBE Camera Depth of Field").setValue(1);
        co.property("ADBE Camera Aperture").setValue(60);
        co.property("ADBE Camera Focus Distance").expression = "length(transform.position, [thisComp.width/2, thisComp.height/2, 0])";
    } catch (e) {}

    // ---------- 7. flou de mouvement + file de rendu ----------
    for (var i = 1; i <= comp.numLayers; i++) {
        try { if (!(comp.layer(i) instanceof CameraLayer)) comp.layer(i).motionBlur = true; } catch (e) {}
    }
    comp.openInViewer();
    app.project.renderQueue.items.add(comp);
    app.endUndoGroup();

    alert("SOGOBA CREATIVE\n\nComposition creee : SOGOBA_TEST_9x16 (10 s)\nAppuie sur Espace pour la previsualiser.\nElle est aussi ajoutee a la file d'attente de rendu.");
})();
