-- icon viewer menu (3ds Max 2025+)
-- Max 2025 rebuilt its menu system: menus can only be added while Max starts up,
-- so the installer copies this file into the user Startup scripts folder.
-- It adds an "Icon Viewer" menu to the main menu bar, just left of "Help".

fn nepre_icon_viewer_menu_cb = (
    local menuMgr = callbacks.notificationParam()
    local mainMenuBar = menuMgr.mainMenuBar
    local helpMenuId = "cee8f758-2199-411b-81e7-d3ff4a80d143"   -- id of Max's Help menu (from Autodesk docs)
    -- these ids are fixed on purpose: Max uses them to remember menu customizations
    local subMenu = mainMenuBar.CreateSubMenu "3E2B7C41-9A5D-4F8E-B1C6-7D2A9E0F4B13" "Icon Viewer" beforeId:helpMenuId
    -- 647394 = the macroscript action table, "macroName`category" = the macroscript to run
    subMenu.CreateAction "5A8C1E92-6B3F-4D7A-9E24-C1F0B8D3A657" 647394 "icon_viewer`NepreTool" title:"MAXIcon Viewer..."
)
callbacks.removeScripts id:#nepreIconViewerMenu
callbacks.addScript #cuiRegisterMenus nepre_icon_viewer_menu_cb id:#nepreIconViewerMenu
