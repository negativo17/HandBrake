%global commit0 b1a4f0dfc2b08590a1a58652287bf052f25ad238
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# Build with "--with ffmpeg" or enable this to use system FFMpeg libraries
# instead of bundled libAV. Unfortunately with FFMpeg UTF-8 subtitles are not
# recognized in media source files. :(
#global _with_ffmpeg 1

# Build with "--with mfx" or enable this to build support for Intel QuickSync
# encoder support. Links and builds fine, but there is no GUI for it.
#global _with_mfx 1

Name:           HandBrake
Version:        1.0
Release:        23%{?shortcommit0:%{shortcommit0}}%{?dist}
Summary:        An open-source multiplatform video transcoder
License:        GPLv2+
URL:            http://handbrake.fr/

Source0:        https://github.com/%{name}/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

# The project fetches libraries to bundle in the executable at compile time; to
# have them available before building, proceed as follows. All files will be
# available in the "download" folder.
#
# ./configure
# cd build
# make contrib.fetch

%{!?_with_ffmpeg:Source10:       https://libav.org/releases/libav-11.3.tar.gz}

# Make bundled FFMpeg patch optional (until FFMpeg 2.9.x):
# https://github.com/HandBrake/HandBrake/pull/32
Patch0:         https://github.com/SeanMcG/HandBrake/commit/cf1571f3bf314638a608784f19f80edb736e8144.patch

BuildRequires:  a52dec-devel >= 0.7.4
BuildRequires:  cmake
BuildRequires:  bzip2-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  fontconfig-devel
%{?_with_ffmpeg:BuildRequires:  ffmpeg-devel >= 2.6}
# Should be >= 2.6:
BuildRequires:  freetype-devel >= 2.4.11
# Should be >= 0.19.7:
BuildRequires:  fribidi-devel >= 0.19.4
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  intltool
BuildRequires:  jansson-devel
BuildRequires:  lame-devel >= 3.98
BuildRequires:  libappindicator-gtk3-devel
# Should be >= 0.13.2:
BuildRequires:  libass-devel >= 0.13.1
# Contains a required patch for HandBrake 1.0:
BuildRequires:  libbluray-devel >= 0.9.3-2
BuildRequires:  libdvdnav-devel >= 5.0.1
BuildRequires:  libdvdread-devel >= 5.0.0
BuildRequires:  libfdk-aac-devel >= 0.1.4
BuildRequires:  libgudev1-devel
%{?_with_mfx:BuildRequires:  libmfx-devel >= 6.0}
BuildRequires:  libmpeg2-devel >= 0.5.1
BuildRequires:  libnotify-devel
BuildRequires:  libogg-devel
BuildRequires:  librsvg2-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  libtheora-devel
BuildRequires:  libtool
BuildRequires:  libvorbis-devel
# Should be >= 1.5:
BuildRequires:  libvpx-devel >= 1.3
BuildRequires:  libxml2-devel
BuildRequires:  m4
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  python
BuildRequires:  subversion
BuildRequires:  tar
BuildRequires:  webkitgtk3-devel
BuildRequires:  wget
BuildRequires:  x264-devel >= 0.148
BuildRequires:  x265-devel >= 1.9
BuildRequires:  yasm
BuildRequires:  zlib-devel
Requires:       hicolor-icon-theme

%description
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

%package gui
Summary:        An open-source multiplatform video transcoder (GUI)
Obsoletes:      HandBrake < %{version}-%{release}
Provides:       HandBrake = %{version}-%{release}
Requires:       hicolor-icon-theme
Requires:       libdvdcss%{_isa}

%description gui
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

This package contains the main program with a graphical interface.

%package cli
Summary:        An open-source multiplatform video transcoder (CLI)
Requires:       libdvdcss%{_isa}

%description cli
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

This package contains the command line version of the program.

%prep
%setup -qn %{name}-%{commit0}
%{?_with_ffmpeg:%patch0 -p1}
mkdir -p download

%{!?_with_ffmpeg:cp %{SOURCE10} download}

# Use system libraries in place of bundled ones
for module in a52dec fdk-aac %{?_with_ffmpeg:ffmpeg} libdvdnav libdvdread libbluray %{?_with_mfx:libmfx} libvpx x265; do
    sed -i -e "/MODULES += contrib\/$module/d" make/include/main.defs
done

%build
echo "HASH=%{commit0}" > version.txt
echo "SHORTHASH=%{shortcommit0}" >> version.txt
echo "DATE=$(date "+%Y-%m-%d %T")" >> version.txt

# This makes build stop if any download is attempted
export http_proxy=http://127.0.0.1

# By default the project is built with optimizations for speed and no debug.
# Override configure settings by passing RPM_OPT_FLAGS and disabling preset
# debug options.
echo "GCC.args.O.speed = %{optflags} %{?_with_ffmpeg:-I%{_includedir}/ffmpeg} -lx265 -lfdk-aac %{?_with_mfx:-lmfx}" > custom.defs
echo "GCC.args.g.none = " >> custom.defs

# Not an autotools configure script.
./configure \
    --build build \
    --prefix=%{_prefix} \
    --verbose \
    --disable-gtk-update-checks \
    %{?_with_mfx:--enable-qsv}

make -C build %{?_smp_mflags}

%install
%make_install -C build
desktop-file-validate %{buildroot}/%{_datadir}/applications/ghb.desktop
%find_lang ghb

%post gui
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &> /dev/null || :

%postun gui
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%posttrans gui
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f ghb.lang gui
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/ghb
%{_datadir}/applications/ghb.desktop
%{_datadir}/icons/hicolor/scalable/apps/hb-icon.svg

%files cli
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/HandBrakeCLI

%changelog
* Sun Jul 03 2016 Simone Caronni <negativo17@gmail.com> - 1.0-23.b1a4f0d
- Update to latest sources.

* Sun Jun 19 2016 Simone Caronni <negativo17@gmail.com> - 1.0-22.221bfe7
- Update to latest sources, bump build requirements.

* Tue May 24 2016 Simone Caronni <negativo17@gmail.com> - 1.0-21.879a512
- Update to latest sources.

* Wed Apr 13 2016 Simone Caronni <negativo17@gmail.com> - 1.0-20.8be786a
- Update to latest sources.
- Update build requirements of x264/x265 to match upstream.

* Thu Mar 31 2016 Simone Caronni <negativo17@gmail.com> - 1.0-19.a447656
- Bugfixes.

* Tue Mar 29 2016 Simone Caronni <negativo17@gmail.com> - 1.0-18.113e2a5
- Update to latest snapshot for various fixes.

* Wed Mar 16 2016 Simone Caronni <negativo17@gmail.com> - 1.0-17.12f7be2
- Update to latest sources.

* Fri Feb 12 2016 Simone Caronni <negativo17@gmail.com> - 1.0-16.0da688d
- Update to latest snapshot.

* Sun Jan 31 2016 Simone Caronni <negativo17@gmail.com> - 1.0-15.ba5eb77
- Update to latest snapshot.

* Fri Jan 22 2016 Simone Caronni <negativo17@gmail.com> - 1.0-14.08e7b54
- Update to latest sources, contains normalization fix.
- Make Intel QuickSync encoder suppport conditional at build time.

* Sat Jan 16 2016 Simone Caronni <negativo17@gmail.com> - 1.0-13.ed8c11e
- Update to latest sources.

* Fri Jan 08 2016 Simone Caronni <negativo17@gmail.com> - 1.0-12.ee1167e
- Update to latest sources.

* Wed Dec 23 2015 Simone Caronni <negativo17@gmail.com> - 1.0-11.1e56395
- Update sources. Intel Quick Sync hardware support can be built using the same
  library as FFMpeg. No frontend support yet.

* Mon Dec 21 2015 Simone Caronni <negativo17@gmail.com> - 1.0-10.57a9f48
- Update sources.

* Fri Dec 11 2015 Simone Caronni <negativo17@gmail.com> - 1.0-9.3443f6a
- Update to latest sources.

* Sun Dec 06 2015 Simone Caronni <negativo17@gmail.com> - 1.0-8.ca69335
- Update to latest sources.

* Tue Dec 01 2015 Simone Caronni <negativo17@gmail.com> - 1.0-7.46e641c
- Switch back to bundled libav 11 to fix subtitle detection.
- Make bundling libav conditional.

* Fri Nov 27 2015 Simone Caronni <negativo17@gmail.com> - 1.0-6.46e641c
- Update to latest sources.

* Mon Nov 23 2015 Simone Caronni <negativo17@gmail.com> - 1.0-5.6c731e1
- Update ffmpeg patch.

* Fri Nov 20 2015 Simone Caronni <negativo17@gmail.com> - 1.0-4.6c731e1
- Update to latest upstream.
- Add license macro.

* Sat Nov 14 2015 Simone Caronni <negativo17@gmail.com> - 1.0-3.6d66bd5
- Use system libfdk-aac.

* Tue Nov 10 2015 Simone Caronni <negativo17@gmail.com> - 1.0-2.6d66bd5
- Update snapshot.
- Use packaging guidelines for GitHub snapshots.
- Update fdk-aac bundle.
- Update build requirements.

* Wed Oct 28 2015 Simone Caronni <negativo17@gmail.com> - 1.0-1
- Update to master branch.
- Use system x265.

* Fri Oct 23 2015 Simone Caronni <negativo17@gmail.com> - 0.10.2-3
- Udpate patches from 0.10.x branch.
- Use system ffmpeg libraries in place of bundled libav.

* Mon Sep 28 2015 Simone Caronni <negativo17@gmail.com> - 0.10.2-2
- Update latest patches from the 0.10.x branch.

* Thu Jun 11 2015 Simone Caronni <negativo17@gmail.com> - 0.10.2-1
- Update to 0.10.2.
- Use handbrake.fr URL for source 0.

* Mon Mar 09 2015 Simone Caronni <negativo17@gmail.com> - 0.10.1-1
- Update to 0.10.1.

* Mon Jan 26 2015 Simone Caronni <negativo17@gmail.com> - 0.10.0-12
- Fix huge icons problem.

* Wed Nov 26 2014 Simone Caronni <negativo17@gmail.com> - 0.10.0-11
- Update to 0.10.0 official release.

* Wed Nov 05 2014 Simone Caronni <negativo17@gmail.com> - 0.10-10.svn6507
- Update to SVN revision 6507.

* Mon Nov 03 2014 Simone Caronni <negativo17@gmail.com> - 0.10-9.svn6502
- Update to SVN revision 6502.

* Fri Oct 24 2014 Simone Caronni <negativo17@gmail.com> - 0.10-8.svn6461
- Update to SVN revision 6461.

* Fri Oct 10 2014 Simone Caronni <negativo17@gmail.com> - 0.10-7.svn6439
- Update to SVN revision 6439.

* Fri Oct 03 2014 Simone Caronni <negativo17@gmail.com> - 0.10-6.svn6422
- Update to SVN revision 6430.

* Sun Sep 28 2014 Simone Caronni <negativo17@gmail.com> - 0.10-5.svn6422
- Update to SVN revision 6422.

* Mon Sep 08 2014 Simone Caronni <negativo17@gmail.com> - 0.10-4.svn6404
- Update to SVN revision 6404.
- Update libdvdread and libdvdnav requirements.

* Mon Sep 08 2014 Simone Caronni <negativo17@gmail.com> - 0.10-3.svn6394
- Update to SVN revision 6394.

* Mon Sep 01 2014 Simone Caronni <negativo17@gmail.com> - 0.10-2.svn6386
- Update to svn revision 6386; new x265 presets.
- Update x265 libraries.

* Sat Aug 23 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-17.svn6304
- Update to svn revision 6351. HandBrake version is now 0.10:
  https://trac.handbrake.fr/milestone/HandBrake%200.10
- Lame and x264 libraries are now linked by default.
- Remove mkv, mpeg2dec and libmkv as they are no longer used.
- LibAV is now enabled by default.
- Add libappindicator-gtk3 build requirement.

* Sun Aug 17 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-16.svn6304
- Update to 6304 snapshot.

* Wed Aug 06 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-15.svn6268
- Update to latest snapshot.

* Wed Jul 30 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-14.svn6244
- Updated to latest snapshot.
- Enable avformat muxer, replaces libmkv and mp4v2 support.
- Requires libdvdnav >= 5.0.0 to fix crashes.
- Remove ExclusiveArch.

* Sat Jul 05 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-13.svn6227
- Updated to SVN snapshot.
- Remove RHEL 6 conditionals.

* Tue Mar 25 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-12
- Backport DVD changes from trunk (should fix libdvdnav crashes with specific
  DVD titles).
- Use system ffpmeg 2 libraries in place of bundled libav.

* Mon Mar 17 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-11
- Fix crash on Fedora.

* Fri Mar 14 2014 Simone Caronni <negativo17@gmail.com> - 0.9.9-10
- Use system libdvdnav/libdvdread.

* Mon Dec 23 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-9
- Use system libraries for libbluray, lame, mpeg2dec, a52dec (patch), libmkv
  (patch), x264 (faac, fdk-aac, libav, libdvdnav, libdvdread and mp4v2 are still
  bundled).
- Use Fedora compiler options.
- Use GStreamer 1.x on Fedora and RHEL/CentOS 7.
- Add fdk-aac support.

* Mon Dec 23 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-8
- Scriptlets need to run for gui subpackage and not base package. Thanks to
  Peter Oliver.

* Mon Sep 09 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-7
- Add requirement on libdvdcss, fix hicolor-icon-theme requirement.

* Fri Jul 26 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-6
- Enable building CLI only on CentOS/RHEL 6.
- Disable GTK update checks (updates come only packaged).

* Tue Jul 23 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-5
- Enable command line interface only for CentOS/RHEL 6.

* Thu May 30 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-4
- Updated x264 to r2282-1db4621 (stable branch) to fix Fedora 19 crash issues.

* Mon May 20 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-3
- Update to 0.9.9.
- Separate GUI and CLI packages.

* Sat May 11 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-2.5449svn
- Updated.

* Wed May 01 2013 Simone Caronni <negativo17@gmail.com> - 0.9.9-1.5433svn
- First build.
