%global commit0 9bd2b8e50ca2e8e0b52580714b54dbca33b809a5
%global date 20180111
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global tag %{version}

%global desktop_id fr.handbrake.ghb

Name:           HandBrake
Version:        1.1.0
Release:        5%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Summary:        An open-source multiplatform video transcoder
License:        GPLv2+
URL:            http://handbrake.fr/

%if 0%{?tag:1}
Source0:        https://download2.handbrake.fr/%{version}/%{name}-%{version}-source.tar.bz2#/%{name}-%{version}.tar.bz2
%else
Source0:        https://github.com/%{name}/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif

# The project fetches libraries to bundle in the executable at compile time; to
# have them available before building, proceed as follows. All files will be
# available in the "download" folder.
#
# ./configure
# cd build
# make contrib.fetch

# Use system OpenCL headers
Patch1:         %{name}-system-OpenCL.patch
# Pass strip tool override to gtk/configure
Patch2:         %{name}-nostrip.patch
# Fix SubRip subtitle issue when built with FFmpeg
Patch3:         https://trac.ffmpeg.org/raw-attachment/ticket/6304/handbrake_subrip.patch#/%{name}-subrip.patch

BuildRequires:  liba52-devel >= 0.7.4
BuildRequires:  cmake
BuildRequires:  bzip2-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  desktop-file-utils
# Should be >= 2.12.1:
BuildRequires:  fontconfig-devel >= 2.10.95
BuildRequires:  ffmpeg-devel >= 4.0
# Should be >= 2.8.1:
BuildRequires:  freetype-devel >= 2.4.11
# Should be >= 0.19.7:
BuildRequires:  fribidi-devel >= 0.19.4
BuildRequires:  gcc
BuildRequires:  gstreamer1-plugins-base-devel
# Should be >= 1.7.2:
BuildRequires:  harfbuzz-devel >= 1.3.2
BuildRequires:  intltool
BuildRequires:  jansson-devel >= 2.10
BuildRequires:  lame-devel >= 3.100
BuildRequires:  libappindicator-gtk3-devel
# Should be >= 0.14.0:
BuildRequires:  libass-devel >= 0.13.4
BuildRequires:  libbluray-devel >= 1.0.2
BuildRequires:  libdvdnav-devel >= 5.0.3
BuildRequires:  libdvdread-devel >= 5.0.3
BuildRequires:  libfdk-aac-devel >= 0.1.5
# On Fedora, libgudev provides libgudev1:
BuildRequires:  libgudev1-devel
# Should be >= 1.23:
BuildRequires:  libmfx-devel >= 1.21
#BuildRequires:  libva-devel
BuildRequires:  libmpeg2-devel >= 0.5.1
BuildRequires:  libnotify-devel
# Should be >= 1.3.2:
BuildRequires:  libogg-devel >= 1.3.0
BuildRequires:  librsvg2-devel
# Should be >= 0.1.9:
BuildRequires:  libsamplerate-devel >= 0.1.8
BuildRequires:  libtheora-devel >= 1.1.1
BuildRequires:  libtool
BuildRequires:  libva-devel
# Should be >= 1.3.5:
BuildRequires:  libvorbis-devel >= 1.3.3
# Should be >= 1.6.1:
BuildRequires:  libvpx-devel >= 1.3
BuildRequires:  libxml2-devel
BuildRequires:  m4
BuildRequires:  make
BuildRequires:  opencl-headers
# Should be >= 1.2.1:
BuildRequires:  opus-devel >= 1.0.2
BuildRequires:  patch
BuildRequires:  python
BuildRequires:  subversion
BuildRequires:  tar
BuildRequires:  wget
BuildRequires:  x264-devel >= 1:0.148
BuildRequires:  x265-devel >= 1:2.6
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
Provides:       handbrake-gui = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       handbrake = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       gstreamer1-plugins-good%{_isa}
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
Provides:       handbrake-cli = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libdvdcss%{_isa}

%description cli
%{name} is a general-purpose, free, open-source, cross-platform, multithreaded
video transcoder software application. It can process most common multimedia
files and any DVD or Bluray sources that do not contain any kind of copy
protection.

This package contains the command line version of the program.

%prep
%autosetup -p1 %{!?tag:-n %{name}-%{commit0}}
mkdir -p download

# Use system libraries in place of bundled ones
for module in a52dec fdk-aac ffmpeg libdvdnav libdvdread libbluray libmfx libvpx x265; do
    sed -i -e "/MODULES += contrib\/$module/d" make/include/main.defs
done
rm libhb/extras/cl{,_platform}.h

# Fix desktop file
sed -i -e 's/%{desktop_id}.svg/%{desktop_id}/g' gtk/src/%{desktop_id}.desktop

%build
echo "HASH=%{commit0}" > version.txt
echo "SHORTHASH=%{shortcommit0}" >> version.txt
echo "DATE=$(date "+%Y-%m-%d %T")" >> version.txt
%if 0%{?tag:1}
echo "TAG=%{tag}" >> version.txt
echo "TAG_HASH=%{commit0}" >> version.txt
%endif

# This makes build stop if any download is attempted
export http_proxy=http://127.0.0.1

# By default the project is built with optimizations for speed and no debug.
# Override configure settings by passing RPM_OPT_FLAGS and disabling preset
# debug options.
echo "GCC.args.O.speed = %{optflags} -I%{_includedir}/ffmpeg -lx265 -lfdk-aac -lmfx" > custom.defs
echo "GCC.args.g.none = " >> custom.defs
echo "GCC.args.strip = " >> custom.defs

# Not an autotools configure script.
./configure \
    --build build \
    --disable-df-fetch \
    --disable-gtk-update-checks \
    --enable-fdk-aac \
    --enable-qsv \
    --enable-x265 \
    --prefix=%{_prefix} \
    --verbose

%make_build -C build V=1

%install
%make_install -C build

# Desktop file, icons and AppStream metadata from FlatPak build (more complete)
rm -f %{buildroot}/%{_datadir}/applications/ghb.desktop \
    %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps/hb-icon.svg

install -D -p -m 644 gtk/src/%{desktop_id}.desktop \
    %{buildroot}/%{_datadir}/applications/%{desktop_id}.desktop
install -D -p -m 644 gtk/src/%{desktop_id}.svg \
    %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps/%{desktop_id}.svg
install -D -p -m 644 gtk/src/%{desktop_id}.appdata.xml \
    %{buildroot}/%{_datadir}/appdata/%{desktop_id}.appdata.xml

desktop-file-validate %{buildroot}/%{_datadir}/applications/%{desktop_id}.desktop

%find_lang ghb

%if 0%{?rhel} == 7
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
%endif

%files -f ghb.lang gui
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/ghb
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_datadir}/appdata/%{desktop_id}.appdata.xml
%else
%exclude %{_datadir}/appdata/%{desktop_id}.appdata.xml
%endif
%{_datadir}/applications/%{desktop_id}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{desktop_id}.svg

%files cli
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/HandBrakeCLI

%changelog
* Mon Apr 30 2018 Simone Caronni <negativo17@gmail.com> - 1.1.0-5
- Update to final 1.1.0 release.
- Update SPEC file.
- Update build requirements.
- Add FFMpeg patch for subtitles, drop libav option.

* Thu Jan 11 2018 Simone Caronni <negativo17@gmail.com> - 1.1.0-4.20180111git9bd2b8e
- Update to latest snapshot.

* Fri Oct 27 2017 Simone Caronni <negativo17@gmail.com> - 1.1.0-3.20171020gitc22e7ed
- Update to latest 1.1 snapshot.
- Adjust GCC flags.

* Tue Aug 22 2017 Simone Caronni <negativo17@gmail.com> - 1.1.0-2.20170819git9fd0481
- Update to latest snapshot.

* Mon Jun 26 2017 Simone Caronni <negativo17@gmail.com> - 1.1.0-1.20170624gitf9f999c
- Update to latest snapshot.

* Sun May 14 2017 Simone Caronni <negativo17@gmail.com> - 1.0.8-1.20170511git7f17f5c
- Update to latest snapshot.
- Provide lowercase handbrake/handbrake-gui and handbrake-cli.
- Add some RPMFusion changes:
  * Invert logic for FFMpeg system builds.
  * Enable QuickSync video only on i686/x86_64.
  * Make FDK-AAC support conditional.
  * Allow building from released version.

* Wed Apr 12 2017 Simone Caronni <negativo17@gmail.com> - 1.0.7-2.20170410git0a8dde9
- Remove webkitgtk3 build requirement, it's actually used only when the update
  checks are enabled in the gui (not needed in our case and removed in fc27).

* Tue Apr 11 2017 Simone Caronni <negativo17@gmail.com> - 1.0.7-1.20170410git0a8dde9
- Update to latest snapshot.

* Wed Mar 22 2017 Simone Caronni <negativo17@gmail.com> - 1.0.3-2.20170318gite4a9a3e
- Update to latest snapshot.
- Apply libbluray patch only where libbluray < 1.0.0.

* Mon Feb 27 2017 Simone Caronni <negativo17@gmail.com> - 1.0.3-1.2017022gitb2f8318
- Update to latest snapshot.

* Tue Jan 24 2017 Simone Caronni <negativo17@gmail.com> - 1.0.2-2.20170123gitc4a14d3
- Update to latest snapshot.
- Fix Intel QSV build.

* Tue Jan 03 2017 Simone Caronni <negativo17@gmail.com> - 1.0.2-1.20170102git063446f
- Update to latest snapshot of the 1.0.x branch.

* Thu Dec 15 2016 Simone Caronni <negativo17@gmail.com> - 1.0-33.20161215gitd58a50a
- Udpate to latest snapshot.

* Thu Dec 01 2016 Simone Caronni <negativo17@gmail.com> - 1.0-32.20161129gitfac5e0e
- Update to latest snapshot.
- Add patches from Dominik Mierzejewski:
  * Allow use of unpatched libbluray.
  * Use system OpenCL headers.
  * Do not strip binaries.

* Fri Nov 18 2016 Simone Caronni <negativo17@gmail.com> - 1.0-31.20161116gitb9c5daa
- Update to latest snapshot.
- Use Flatpak desktop file, icon and AppStream metadata (more complete).

* Sat Oct 08 2016 Simone Caronni <negativo17@gmail.com> - 1.0-30.20161006git88807bb
- Fix date.
- Rebuild for fdk-aac update.

* Sat Oct 08 2016 Simone Caronni <negativo17@gmail.com> - 1.0-29.20160929git88807bb
- Require x265 hotfix.

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 1.0-28.20160929gitd398531
- Rebuild for x265 update.

* Sun Oct 02 2016 Simone Caronni <negativo17@gmail.com> - 1.0-27.20160929gitd398531
- Update to latest snapshot.
- Update package release according to package guidelines.
- Enable Intel Quick Sync Video encoding by default (libmfx package in main
  repositories).
- Add AppData support for Fedora (metadata from upstream).
- Do not run update-desktop-database on Fedora 25+ as per packaging guidelines.

* Fri Aug 05 2016 Simone Caronni <negativo17@gmail.com> - 1.0-26.6b5d91a
- Update to latest sources.

* Thu Jul 14 2016 Simone Caronni <negativo17@gmail.com> - 1.0-25.56c7ee7
- Update to latest snapshot.

* Fri Jul 08 2016 Simone Caronni <negativo17@gmail.com> - 1.0-24.0fc54d0
- Update to latest sources.

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
