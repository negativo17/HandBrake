%global commit0 2e91369bae27841e0ffdcbe2e0fac2aaa7e779cf
%global date 20231008
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global tag %{version}

%global desktop_id fr.handbrake.ghb

Name:           HandBrake
Version:        1.7.3
Release:        1%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Summary:        An open-source multiplatform video transcoder
License:        GPLv2+
URL:            http://handbrake.fr/

%if 0%{?tag:1}
Source0:        https://github.com/%{name}/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
%else
Source0:        https://github.com/%{name}/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif

# Adjust dependencies when using system libraries
Patch0:         %{name}-deps.patch

BuildRequires:  AMF-devel
BuildRequires:  appstream
BuildRequires:  bzip2-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  fontconfig-devel
BuildRequires:  libavcodec-devel >= 6.1.1
BuildRequires:  libavfilter-devel >= 6.1.1
BuildRequires:  libavformat-devel >= 6.1.1
BuildRequires:  libdovi-devel >= 3.1.2
BuildRequires:  freetype-devel >= 2.4.11
BuildRequires:  fribidi-devel >= 0.19.4
BuildRequires:  gcc-c++
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  harfbuzz-devel >= 1.3.2
BuildRequires:  intltool
BuildRequires:  jansson-devel >= 2.10
BuildRequires:  lame-devel >= 3.100
BuildRequires:  liba52-devel >= 0.7.4
BuildRequires:  libappindicator-gtk3-devel
BuildRequires:  libappstream-glib
BuildRequires:  libass-devel >= 0.13.4
BuildRequires:  libbluray-devel >= 1.0.2
BuildRequires:  libdav1d-devel >= 0.3.0
BuildRequires:  libdrm-devel
BuildRequires:  libdvdnav-devel >= 5.0.3
BuildRequires:  libdvdread-devel >= 5.0.3
BuildRequires:  libfdk-aac-devel >= 2.0.1
BuildRequires:  libgudev1-devel
BuildRequires:  libva-devel
BuildRequires:  libmpeg2-devel >= 0.5.1
BuildRequires:  libnotify-devel
BuildRequires:  libogg-devel >= 1.3.0
BuildRequires:  librsvg2-devel
BuildRequires:  libsamplerate-devel >= 0.1.8
BuildRequires:  libtheora-devel >= 1.1.1
BuildRequires:  libtool
BuildRequires:  libva-devel
BuildRequires:  libvorbis-devel >= 1.3.3
BuildRequires:  libvpx-devel >= 1.7.0
BuildRequires:  libxml2-devel
BuildRequires:  m4
BuildRequires:  make
BuildRequires:  meson
BuildRequires:  nv-codec-headers >= 11
BuildRequires:  opus-devel >= 1.3
BuildRequires:  patch
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.16
BuildRequires:  pkgconfig(numa)
BuildRequires:  python3
BuildRequires:  speex-devel >= 1.2
BuildRequires:  svt-av1-devel
BuildRequires:  tar
BuildRequires:  turbojpeg-devel >= 1.5.3
BuildRequires:  wget
BuildRequires:  x264-devel >= 1:0.155
BuildRequires:  x265-devel >= 1:3.2.1
BuildRequires:  zlib-devel
BuildRequires:  xz-devel
BuildRequires:  zimg-devel >= 3.0.1

%ifarch x86_64
BuildRequires:  intel-mediasdk-devel
BuildRequires:  oneVPL-devel
%endif

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
%if 0%{?tag:1}
%autosetup -p1
%else
%autosetup -p1 -n %{name}-%{commit0}
%endif
mkdir -p download build/contrib/include

# Use system libraries in place of bundled ones
for module in fdk-aac ffmpeg libdav1d libdovi libdvdnav libdvdread libbluray libmfx libvpl nvenc svt-av1 x265 zimg; do
    sed -i -e "/MODULES += contrib\/$module/d" make/include/main.defs
done

%build
echo "HASH=%{commit0}" > version.txt
echo "SHORTHASH=%{shortcommit0}" >> version.txt
echo "DATE=$(date "+%Y-%m-%d %T")" >> version.txt
%if 0%{?tag:1}
echo "TAG=%{tag}" >> version.txt
echo "TAG_HASH=%{commit0}" >> version.txt
%endif

# This makes the build stop if any download is attempted
export http_proxy=http://127.0.0.1
export https_proxy=http://127.0.0.1

# By default the project is built with optimizations for speed and no debug.
# Override configure settings by passing RPM_OPT_FLAGS and disabling preset
# debug options.
# These plus "--no-harden" at configure time set proper compiler flags:
cat > custom.defs << EOF
GCC.args.c_std =
GCC.args.cxx_std =
GCC.args.O.speed = %build_cflags -I%{_includedir}/vpl
GCC.args.g.none =
GCC.args.strip =
EOF

# Not an autotools configure script:
./configure \
    --build build \
    --disable-df-fetch \
    --disable-df-verify \
    --disable-update-checks \
    --enable-asm \
    --enable-fdk-aac \
    --enable-ffmpeg-aac \
    --enable-gst \
    --enable-libdovi \
    --enable-numa \
    --enable-nvdec \
    --enable-nvenc \
%ifarch x86_64
    --enable-qsv \
%endif
    --enable-vce \
    --enable-x265 \
    --force \
    --no-harden \
    --prefix=%{_prefix}

%make_build -C build

%install
%make_install -C build

%find_lang ghb

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{desktop_id}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml

%files -f ghb.lang gui
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/ghb
%{_metainfodir}/%{desktop_id}.metainfo.xml
%{_datadir}/applications/%{desktop_id}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{desktop_id}.svg

%files cli
%license COPYING
%doc AUTHORS.markdown NEWS.markdown README.markdown THANKS.markdown
%{_bindir}/HandBrakeCLI

%changelog
* Tue Feb 20 2024 Simone Caronni <negativo17@gmail.com> - 1.7.3-1
- Update to 1.7.3.

* Tue Jan 16 2024 Simone Caronni <negativo17@gmail.com> - 1.7.2-1
- Update to version 1.7.2.

* Mon Oct 09 2023 Simone Caronni <negativo17@gmail.com> - 1.7.0-3.20231008git2e91369
- Update to latest snapshot.

* Thu Sep 07 2023 Simone Caronni <negativo17@gmail.com> - 1.7.0-2.20230906gitc9fc5c3
- Update to latest snapshot.

* Wed Jun 07 2023 Simone Caronni <negativo17@gmail.com> - 1.7.0-1.20230606git8e8f068
- Update to latest 1.7.0 snapshot.

* Mon Jun 05 2023 Simone Caronni <negativo17@gmail.com> - 1.6.2-4.20230604git131bdd6
- Update to latest 1.6.x branch snapshot.
- Remove wrongly applied patch.

* Mon May 29 2023 Simone Caronni <negativo17@gmail.com> - 1.6.2-3.20230310gitaf134d2
- Adjust configure options.

* Fri Mar 17 2023 Simone Caronni <negativo17@gmail.com> - 1.6.2-2.20230310gitaf134d2
- Remove leftovers from GCC settings.

* Tue Mar 14 2023 Simone Caronni <negativo17@gmail.com> - 1.6.2-1.20230310gitaf134d2
- Update to latest 1.6.2 snapshot.

* Fri Feb 24 2023 Simone Caronni <negativo17@gmail.com> - 1.6.1-2
- Update to official 1.6.1 release with patches.

* Mon Jan 09 2023 Simone Caronni <negativo17@gmail.com> - 1.6.1-1.20230108git6faee60
- Update to latest 1.6.1 snapshot.

* Mon Jan 09 2023 Simone Caronni <negativo17@gmail.com> - 1.6.0-7
- Update to final 1.6.0 release.

* Thu Dec 08 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-6.20221208gita698e53
- Update to latest snapshot.

* Sun Oct 09 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-5.20221005gitd026bcf
- Update snapshot.

* Wed Sep 21 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-4.20220920git7f9f39b
- Update to latest snapshot.

* Tue Jul 05 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-3.20220702gitf8e5306
- Update to latest snapshot.

* Tue Apr 26 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-2.20220425gitf5f6fcd
- Update to latest 1.6.0 snapshot.
- Set proper compile options.

* Thu Apr 07 2022 Simone Caronni <negativo17@gmail.com> - 1.6.0-1.20220407gitd719d8a
- Update to latest 1.6.0 snapshot.
- Adjust dependencies when using system libraries.
- Adjust compile options for changed defaults.

* Fri Feb 11 2022 Simone Caronni <negativo17@gmail.com> - 1.5.1-2
- Enable Advanced Media Framework support.

* Sat Feb 05 2022 Simone Caronni <negativo17@gmail.com> - 1.5.1-1
- Update to 1.5.1.
- Enable One Video Processing Library.
- Drop RHEL/CentOS 7 support.
- Enable AppData for RHEL/CentOS 8.

* Sun Nov 07 2021 Simone Caronni <negativo17@gmail.com> - 1.4.2-1
- Update to 1.4.2.

* Wed Sep 29 2021 Simone Caronni <negativo17@gmail.com> - 1.4.1-3
- Fix build on aarch64.
- Update SPEC file.

* Fri Sep 24 2021 Simone Caronni <negativo17@gmail.com> - 1.4.1-2
- Update to final 1.4.1.

* Sun Aug 15 2021 Simone Caronni <negativo17@gmail.com> - 1.4.1-1.20210814git00d42bf
- Update to latest 1.4.x snapshot.

* Mon Jul 26 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-7
- Rebuild for updated dependencies.

* Tue Jul 20 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-6
- Update to 1.4.0 final release.

* Tue Apr 27 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-5.20210422git48e9fbf
- Update to latest snapshot.

* Thu Mar 25 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-4.20210324git2b18fe2
- Update to latest snapshot.

* Mon Mar 01 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-3.20210301git3235f63
- Update to latest snapshot.

* Thu Jan 28 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-2.20210125git818dbfe
- Update to latest snapshot.

* Wed Jan  6 2021 Simone Caronni <negativo17@gmail.com> - 1.4.0-1.20210105git2e305ed
- Update to latest 1.4.0 snapshot.

* Sun Dec 06 2020 Simone Caronni <negativo17@gmail.com> - 1.3.3-4
- Rebuild for updated depdendencies.

* Wed Jul 15 2020 Simone Caronni <negativo17@gmail.com> - 1.3.3-3
- Rebuild for updated dependencies.

* Thu Jul 09 2020 Simone Caronni <negativo17@gmail.com> - 1.3.3-2
- Rebuild for updated dependencies.

* Tue Jun 23 2020 Simone Caronni <negativo17@gmail.com> - 1.3.3-1
- Update to 1.3.3.
- Add temporary patch to Makefile.
- Trim changelog.
- Disable metainfo generation on CentOS/RHEL 7/8 as gettext is too old.

* Fri May 15 2020 Simone Caronni <negativo17@gmail.com> - 1.3.2-1
- Update to 1.3.2 release.

* Wed Apr 15 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-4.20200331gitbbcd3a5
- Update to latest 1.3.x branch snapshot.
- Enable Intel QuickSync support.

* Wed Mar 18 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-3
- Rebuild for updated dependencies.

* Sun Jan 19 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-2
- Rebuild for updated dependencies.

* Sun Jan 12 2020 Simone Caronni <negativo17@gmail.com> - 1.3.1-1
- Update to 1.3.1.

* Mon Dec 09 2019 Simone Caronni <negativo17@gmail.com> - 1.3.0-1
- Update to 1.3.0.

* Wed Nov 27 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-8.20191031gita5d359d
- Update to latest snapshot.

* Fri Nov 01 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-7.20191031gitad8cf9f
- Update to latest snapshot.
- Momentarily disable QSV encoder.

* Sun Oct 20 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-6.20191018git9901594
- Udpate to latest snapshot and dependencies.

* Sat Sep 14 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-5.20190914gite2a9571
- Update to latest snapshot.

* Thu Sep 12 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-4
- Add patches from the 1.2.x branch.

* Sun Jul 07 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-3
- Rebuild for updated dependencies.

* Mon May 27 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-2
- Rebuild for updated dependencies.

* Sun Mar 03 2019 Simone Caronni <negativo17@gmail.com> - 1.2.2-1
- Update to 1.2.2.

* Thu Feb 28 2019 Simone Caronni <negativo17@gmail.com> - 1.2.1-2
- Rebuild for updated dependencies.

* Sat Feb 23 2019 Simone Caronni <negativo17@gmail.com> - 1.2.1-1
- Update to 1.2.1.
- Do not install AppData file on RHEL < 8.
