(

rollout installer_rl "icon viewer installation" (
    -- 3ds Max 2025 = release 27000. From 2025 on, menuMan was removed and replaced by a new menu system.
    local is_new_menu_system = ((maxVersion())[1] >= 27000)
    local menu_startup_file = (getDir #userStartupScripts) + @"\icon_viewer_menu.ms"

    fn get_script_menu = (
        local main_menu = menuman.getmainmenubar()
        local script_menu = undefined
        for i=1 to main_menu.numitems() do (
            local item = main_menu.getitem i
            local item_name = item.gettitle()
            if  item_name == "&Scripting" do (
                script_menu  = item.getSubMenu()
                break
            )
        )
        script_menu
    )


    fn remove_menu = (
        if is_new_menu_system do (
            -- 2025+: the menu comes from a startup script, so delete it and its callback
            callbacks.removeScripts id:#nepreIconViewerMenu
            if doesFileExist menu_startup_file do deleteFile menu_startup_file
            return ok
        )
        local script_menu = get_script_menu()
        if not script_menu==undefined do (
            -- remove item
            for i=script_menu.numitems() to 1 by -1 do (
                local item = script_menu.getitem i
                local item_name = item.gettitle()
                if item_name == "MAXIcon &Viewer..." do (
                    script_menu.removeitembyposition i
                )
            )
        )
        menuman.updatemenubar()
    )

    local script_folder_name = "icon_viewer"

    fn add_menu = (
        if is_new_menu_system do (
            -- 2025+: copy the menu startup script; the menu appears after Max restarts
            local root = getfilenamepath (getthisscriptfilename())
            makeDir (getDir #userStartupScripts) all:true
            copyFile (root + "icon_viewer_menu.ms") menu_startup_file
            return ok
        )
        -- add item (Max 2024 and older)
        local script_menu = get_script_menu()
        local item = menuman.createactionitem "icon_viewer" "NepreTool"
        item.settitle "MAXIcon &Viewer..."
        item.setusecustomtitle true

        local item_count = script_menu.numitems()
        local index = item_count + 1
        for i=1 to item_count do (
            local item = script_menu.getitem i
            local item_name = item.gettitle()
            if item_name == "MAXScript &Editor..." do (
                index = i+1
                break
            )
        )

        script_menu.addItem item index
        menuman.updatemenubar()
    )

    button install_btn "install icon viewer" width:250 height:40
    group "option" (
        checkbox menu_cbk "add menu entry (2025+: after restart)" checked:true
    )
    button uninstall_btn "uninstall" width:250 height:25


    on install_btn pressed do (
        local root = getfilenamepath (getthisscriptfilename())

        -- copy scripts files
        hiddendoscommand ("xcopy " + "\"" + root + "icon_viewer\" \"" +(getdir #userscripts)+ @"\python\icon_viewer\"+ "\" /y /h /d /s /r /q") prompt:"copy scripts files"
        hiddendoscommand ("xcopy " + "\"" + root+ "3dsmax.png\" \"" +(getdir #usericons)+ @"\dark\icon_viewer\" + "\" /y /h /d /s /r /q") prompt:"copy icon"
        hiddendoscommand ("xcopy " + "\"" + root+ "3dsmax.png\" \"" +(getdir #usericons)+ @"\light\icon_viewer\" + "\" /y /h /d /s /r /q") prompt:"copy icon"

        -- macros
        macroscript icon_viewer buttontext:"icon viewer" category:"NepreTool" iconname:"icon_viewer/3dsmax" (
            on execute do (
                local scripts_dir = (getdir #userscripts) + @"\python"
                python.execute(@"import sys; sys.path.append(r'" +scripts_dir + @"') if not r'" +scripts_dir+ @"' in sys.path else None")
                local icon_viwer = python.import "icon_viewer"
                icon_viwer.show()
            )
        )

        remove_menu()

        if menu_cbk.checked do add_menu()

        rollout result_rl "icon viewer installed" (
            group "where to find this tool" (
                label macro_lab "in category: nepretool>icon_viewer" align:#left
                label menu_lab  "or in the menu bar (Max 2025+: restart first)"  align:#left visible:menu_cbk.checked
            )
            button run_btn "run it now!" width:250 height:30
            on run_btn pressed do (
                macros.run "NepreTool" "icon_viewer"
                destroydialog result_rl
            )
        )

        createdialog result_rl width:260
        destroydialog installer_rl

    )

    on uninstall_btn pressed do (
        hiddendoscommand ("rmdir /s /q \"" + ((getdir #userscripts) + @"\python\icon_viewer\") + "\"")  prompt:"delete scripts files"
        hiddenDOSCommand ("del \"" +((getdir #userMacros)+@"\NepreTool-icon_viewer.mcr") + "\"")  prompt:"delete macros"
        hiddendoscommand ("rmdir /s /q \"" +(getdir #usericons)+ @"\dark\icon_viewer\"  + "\"")  prompt:"delete icon"
        hiddendoscommand ("rmdir /s /q \"" +(getdir #usericons)+ @"\light\icon_viewer\" + "\"")  prompt:"delete icon"

        remove_menu()
        messagebox ("icon viewer is now removed from current 3ds max.\nthanks for using and take care.") title:"icon viewer uninstallation" beep:off
        destroydialog installer_rl

    )

)

createdialog installer_rl width:260


)